from __future__ import annotations

from collections.abc import Callable

from ..config import Settings
from .base import LLM, Message
from .temp_main_llm import TempMainLLM

# LLM_PROVIDER value in .env  ->  function that builds the adapter.
# Add your own adapters here, e.g. "openai": lambda s: OpenAIChat(...).
PROVIDERS: dict[str, Callable[[Settings], LLM]] = {
    "temp": lambda settings: TempMainLLM(),
}


def create_llm(settings: Settings) -> LLM:
    try:
        factory = PROVIDERS[settings.llm_provider]
    except KeyError:
        raise ValueError(
            f"Unknown LLM_PROVIDER={settings.llm_provider!r}. "
            f"Available: {', '.join(PROVIDERS)}"
        ) from None
    return factory(settings)


__all__ = ["LLM", "Message", "TempMainLLM", "create_llm"]
