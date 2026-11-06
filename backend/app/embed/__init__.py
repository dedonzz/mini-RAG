from __future__ import annotations

from collections.abc import Callable

from ..config import Settings
from .base import Embedder
from .temp_embed import TempEmbed

# EMBED_PROVIDER value in .env  ->  function that builds the embedder.
PROVIDERS: dict[str, Callable[[Settings], Embedder]] = {
    "temp": lambda settings: TempEmbed(settings.embed_model),
}


def create_embedder(settings: Settings) -> Embedder:
    try:
        factory = PROVIDERS[settings.embed_provider]
    except KeyError:
        raise ValueError(
            f"Unknown EMBED_PROVIDER={settings.embed_provider!r}. "
            f"Available: {', '.join(PROVIDERS)}"
        ) from None
    return factory(settings)


__all__ = ["Embedder", "TempEmbed", "create_embedder"]
