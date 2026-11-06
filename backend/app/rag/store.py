"""A tiny vector store: a numpy matrix + a JSON list of chunk records.

Row i of `vectors.npy` is the embedding of `chunks.json[i]`. Search is a
brute-force dot product, which equals cosine similarity because embeddings
are normalised. That's fast enough for tens of thousands of chunks.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


@dataclass
class Chunk:
    doc_id: str  # the file name
    index: int  # position of the chunk within its document
    text: str


@dataclass
class Hit:
    chunk: Chunk
    score: float


class VectorStore:
    def __init__(self, index_dir: Path | None = None) -> None:
        self.index_dir = index_dir
        self.chunks: list[Chunk] = []
        self.vectors = np.zeros((0, 0), dtype=np.float32)
        # Name of the embedder that produced `vectors`.
        self.embedder_name: str | None = None

    def __len__(self) -> int:
        return len(self.chunks)

    def add(self, chunks: list[Chunk], vectors: np.ndarray, embedder_name: str) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")
        if not chunks:
            return
        if len(self.chunks) == 0:
            self.vectors = vectors.astype(np.float32)
        else:
            if vectors.shape[1] != self.vectors.shape[1]:
                raise ValueError("embedding dimension mismatch; rebuild the index")
            self.vectors = np.vstack([self.vectors, vectors.astype(np.float32)])
        self.chunks.extend(chunks)
        self.embedder_name = embedder_name

    def delete_doc(self, doc_id: str) -> int:
        keep = [i for i, c in enumerate(self.chunks) if c.doc_id != doc_id]
        removed = len(self.chunks) - len(keep)
        self.chunks = [self.chunks[i] for i in keep]
        self.vectors = self.vectors[keep] if keep else np.zeros((0, 0), dtype=np.float32)
        return removed

    def clear(self) -> None:
        self.chunks = []
        self.vectors = np.zeros((0, 0), dtype=np.float32)
        self.embedder_name = None

    def search(self, query_vector: np.ndarray, top_k: int) -> list[Hit]:
        if not self.chunks or top_k <= 0:
            return []
        scores = self.vectors @ query_vector
        top_k = min(top_k, len(scores))
        # argpartition finds the top k in O(n); then sort just those k.
        best = np.argpartition(-scores, top_k - 1)[:top_k]
        best = best[np.argsort(-scores[best])]
        return [Hit(self.chunks[i], float(scores[i])) for i in best]

    def chunk_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for c in self.chunks:
            counts[c.doc_id] = counts.get(c.doc_id, 0) + 1
        return counts

    # --- persistence -----------------------------------------------------

    def save(self) -> None:
        if self.index_dir is None:
            return
        self.index_dir.mkdir(parents=True, exist_ok=True)
        np.save(self.index_dir / "vectors.npy", self.vectors)
        payload = {
            "embedder_name": self.embedder_name,
            "chunks": [asdict(c) for c in self.chunks],
        }
        (self.index_dir / "chunks.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )

    def load(self) -> None:
        if self.index_dir is None:
            return
        chunks_path = self.index_dir / "chunks.json"
        vectors_path = self.index_dir / "vectors.npy"
        if not (chunks_path.exists() and vectors_path.exists()):
            return
        payload = json.loads(chunks_path.read_text(encoding="utf-8"))
        self.embedder_name = payload["embedder_name"]
        self.chunks = [Chunk(**c) for c in payload["chunks"]]
        self.vectors = np.load(vectors_path)
