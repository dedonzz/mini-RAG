"""The one interface every LLM adapter implements.

To plug in a real provider, write a class with these attributes/methods
(see README "接上真正的 LLM"), then register it in `app/llm/__init__.py`.
"""

from __future__ import annotations

from typing import Literal, Protocol, TypedDict


class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class LLM(Protocol):
    # Shown in the UI so you can see which implementation is active.
    name: str
    # False only for placeholders like TempMainLLM; the UI then shows a notice
    # instead of treating the output as a real answer.
    configured: bool

    def generate(self, messages: list[Message]) -> str: ...
