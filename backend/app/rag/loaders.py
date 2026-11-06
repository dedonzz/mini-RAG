"""Turn a file into plain text. Add a new format by adding to LOADERS."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path


def _load_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8", errors="replace")


def _load_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(path)
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


LOADERS: dict[str, Callable[[Path], str]] = {
    ".txt": _load_text,
    ".md": _load_text,
    ".pdf": _load_pdf,
}


def is_supported(filename: str) -> bool:
    return Path(filename).suffix.lower() in LOADERS


def load_file(path: Path) -> str:
    return LOADERS[path.suffix.lower()](path)
