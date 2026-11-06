from __future__ import annotations

import numpy as np


class TempEmbed:
    """Local embeddings via sentence-transformers. Free, runs on your machine.

    The model downloads on first use (~470MB for the default) and is cached
    under ~/.cache/huggingface afterwards.
    """

    def __init__(self, model_name: str) -> None:
        self.name = f"TempEmbed ({model_name})"
        self._model_name = model_name
        self._model = None
        # e5-family models are trained with these prefixes.
        is_e5 = "e5" in model_name.lower()
        self._doc_prefix = "passage: " if is_e5 else ""
        self._query_prefix = "query: " if is_e5 else ""

    def _load(self):
        if self._model is None:
            # Imported lazily: torch takes a few seconds to import.
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        vectors = self._load().encode(
            [self._doc_prefix + t for t in texts],
            normalize_embeddings=True,
            batch_size=32,
        )
        return np.asarray(vectors, dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        vector = self._load().encode(
            self._query_prefix + text, normalize_embeddings=True
        )
        return np.asarray(vector, dtype=np.float32)
