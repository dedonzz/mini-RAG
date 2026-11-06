from __future__ import annotations

from .base import Message


class TempMainLLM:
    """Placeholder used until you have an API key.

    It doesn't call any model: it echoes the final user message (the assembled
    prompt) back, and reports `configured = False` so the UI knows to show
    "LLM not configured" plus the retrieved sources and prompt.
    """

    name = "TempMainLLM"
    configured = False

    def generate(self, messages: list[Message]) -> str:
        return messages[-1]["content"] if messages else ""
