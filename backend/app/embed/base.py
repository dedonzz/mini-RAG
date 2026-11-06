"""The interface every embedding implementation follows.

Documents and queries are embedded through separate methods because many
models (including the default e5 model) expect different prefixes for each.
Vectors must be L2-normalised so a dot product equals cosine similarity.
"""

from __future__ import annotations

from typing import Protocol

import numpy as np


class Embedder(Protocol):
    # Identifies the model. Stored with the index so we can tell when the
    # index was built with a different model and needs rebuilding.
    name: str

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        """Return an array of shape (len(texts), dim), float32, normalised."""
        ...

    def embed_query(self, text: str) -> np.ndarray:
        """Return an array of shape (dim,), float32, normalised."""
        ...
