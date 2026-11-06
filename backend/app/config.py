"""Settings.

Two kinds of settings live here:

* `Settings` — read once from `.env` at startup (providers, model names, paths,
  API keys). Changing these requires a restart.
* `RuntimeSettings` — tweakable from the UI (chunk size, overlap, top-k) and
  persisted to `data/settings.json`.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    embed_provider: str
    embed_model: str
    data_dir: Path
    max_upload_mb: int

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def index_dir(self) -> Path:
        return self.data_dir / "index"

    @property
    def runtime_settings_path(self) -> Path:
        return self.data_dir / "settings.json"


def load_settings() -> Settings:
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    if not data_dir.is_absolute():
        data_dir = PROJECT_ROOT / data_dir
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "temp"),
        embed_provider=os.getenv("EMBED_PROVIDER", "temp"),
        embed_model=os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-small"),
        data_dir=data_dir,
        max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "20")),
    )


@dataclass
class RuntimeSettings:
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k: int = 4

    def validate(self) -> None:
        if not 50 <= self.chunk_size <= 4000:
            raise ValueError("chunk_size_out_of_range")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("chunk_overlap_out_of_range")
        if not 1 <= self.top_k <= 20:
            raise ValueError("top_k_out_of_range")

    @classmethod
    def load(cls, path: Path) -> "RuntimeSettings":
        if path.exists():
            return cls(**json.loads(path.read_text(encoding="utf-8")))
        return cls()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
