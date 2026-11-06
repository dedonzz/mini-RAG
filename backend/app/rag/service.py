"""Ties loaders, chunker, embedder, store, prompt and LLM together.

Ingest:  file -> text -> chunks -> vectors -> store
Ask:     question -> query vector -> top-k chunks -> prompt -> LLM -> answer
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ..config import RuntimeSettings, Settings
from ..embed.base import Embedder
from ..llm.base import LLM, Message
from .chunker import chunk_text
from .loaders import load_file
from .prompt import build_messages
from .store import Chunk, Hit, VectorStore


class IngestError(Exception):
    """Raised with a machine-readable code that the frontend translates."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass
class Answer:
    answer: str
    llm_configured: bool
    hits: list[Hit]
    messages: list[Message]


class RagService:
    def __init__(self, settings: Settings, embedder: Embedder, llm: LLM) -> None:
        self.settings = settings
        self.embedder = embedder
        self.llm = llm
        self.runtime = RuntimeSettings.load(settings.runtime_settings_path)
        self.store = VectorStore(settings.index_dir)
        self.store.load()
        settings.uploads_dir.mkdir(parents=True, exist_ok=True)
        # Uploads, deletes and reindexing modify the store; serialise them.
        self._lock = threading.Lock()

    # --- status ------------------------------------------------------------

    @property
    def needs_reindex(self) -> bool:
        """True if the index was built with a different embedding model."""
        return len(self.store) > 0 and self.store.embedder_name != self.embedder.name

    def list_documents(self) -> list[dict]:
        counts = self.store.chunk_counts()
        docs = []
        for path in sorted(self.settings.uploads_dir.iterdir()):
            if not path.is_file() or path.name.startswith("."):
                continue
            stat = path.stat()
            docs.append(
                {
                    "doc_id": path.name,
                    "size_bytes": stat.st_size,
                    "uploaded_at": datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).isoformat(),
                    "chunks": counts.get(path.name, 0),
                }
            )
        return docs

    # --- ingest ------------------------------------------------------------

    def _index_file(self, path: Path) -> int:
        text = load_file(path)
        pieces = chunk_text(text, self.runtime.chunk_size, self.runtime.chunk_overlap)
        if not pieces:
            raise IngestError("empty_text")
        vectors = self.embedder.embed_documents(pieces)
        chunks = [Chunk(doc_id=path.name, index=i, text=t) for i, t in enumerate(pieces)]
        self.store.add(chunks, vectors, self.embedder.name)
        return len(chunks)

    def ingest(self, filename: str, content: bytes) -> int:
        """Save the file (overwriting a same-named one) and index it."""
        path = self.settings.uploads_dir / filename
        with self._lock:
            path.write_bytes(content)
            self.store.delete_doc(filename)
            try:
                count = self._index_file(path)
            except Exception:
                path.unlink(missing_ok=True)
                self.store.save()
                raise
            self.store.save()
            return count

    def delete(self, doc_id: str) -> bool:
        path = self.settings.uploads_dir / doc_id
        with self._lock:
            existed = path.exists()
            path.unlink(missing_ok=True)
            removed = self.store.delete_doc(doc_id)
            self.store.save()
            return existed or removed > 0

    def reindex(self) -> dict[str, str]:
        """Re-chunk and re-embed every uploaded file with current settings.

        Returns {doc_id: error_code} for files that failed.
        """
        errors: dict[str, str] = {}
        with self._lock:
            self.store.clear()
            for doc in self.list_documents():
                try:
                    self._index_file(self.settings.uploads_dir / doc["doc_id"])
                except IngestError as e:
                    errors[doc["doc_id"]] = e.code
                except Exception:
                    errors[doc["doc_id"]] = "load_failed"
            self.store.save()
        return errors

    # --- settings ----------------------------------------------------------

    def update_runtime(self, new: RuntimeSettings) -> None:
        new.validate()
        self.runtime = new
        new.save(self.settings.runtime_settings_path)

    # --- ask ---------------------------------------------------------------

    def ask(self, question: str, top_k: int | None = None) -> Answer:
        k = top_k if top_k is not None else self.runtime.top_k
        hits = self.store.search(self.embedder.embed_query(question), k) if len(self.store) else []
        messages = build_messages(question, hits)
        answer = self.llm.generate(messages)
        return Answer(answer, self.llm.configured, hits, messages)
