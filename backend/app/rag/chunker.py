"""Split text into overlapping chunks without cutting sentences in half.

Algorithm:
1. Break the text into "pieces": sentences (ending in 。！？!? or ". ") and lines.
   Any piece longer than `size` is hard-split.
2. Greedily pack pieces into a chunk until the next one would exceed `size`.
3. Start the next chunk with the trailing pieces of the previous chunk that fit
   in `overlap` characters, so context isn't lost at the boundary. If even the
   last piece is longer than `overlap`, fall back to its last `overlap` chars.
"""

from __future__ import annotations

import re

# Split *after* sentence-ending punctuation or a newline (delimiters are kept).
_BOUNDARY = re.compile(r"(?<=[。！？!?\n])|(?<=\.\s)")


def _pieces(text: str, size: int) -> list[str]:
    pieces: list[str] = []
    for piece in _BOUNDARY.split(text):
        if not piece:
            continue
        for start in range(0, len(piece), size):
            pieces.append(piece[start : start + size])
    return pieces


def _tail(pieces: list[str], overlap: int) -> list[str]:
    """Trailing pieces whose total length fits in `overlap`."""
    if overlap == 0 or not pieces:
        return []
    tail: list[str] = []
    total = 0
    for piece in reversed(pieces):
        if total + len(piece) > overlap:
            break
        tail.insert(0, piece)
        total += len(piece)
    if not tail:
        tail = [pieces[-1][-overlap:]]
    return tail


def chunk_text(text: str, size: int = 500, overlap: int = 100) -> list[str]:
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 <= overlap < size:
        raise ValueError("overlap must be in [0, size)")

    text = re.sub(r"\n{3,}", "\n\n", text.replace("\r\n", "\n")).strip()
    if not text:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    has_new = False  # does `current` contain anything beyond the overlap?

    for piece in _pieces(text, size):
        if current_len + len(piece) > size and has_new:
            chunks.append("".join(current).strip())
            current = _tail(current, overlap)
            current_len = sum(len(p) for p in current)
            has_new = False
        # Drop overlap from the front if it leaves no room for the new piece.
        while current and current_len + len(piece) > size:
            current_len -= len(current.pop(0))
        current.append(piece)
        current_len += len(piece)
        has_new = True

    if has_new:
        chunks.append("".join(current).strip())
    return [c for c in chunks if c]
