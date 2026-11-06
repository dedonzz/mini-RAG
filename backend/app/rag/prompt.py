"""Assemble the messages sent to the LLM from a question + retrieved chunks."""

from __future__ import annotations

from ..llm.base import Message
from .store import Hit

SYSTEM_PROMPT = """You are a helpful assistant answering questions about the user's documents.
Use only the information in the provided context.
If the context does not contain the answer, say that you don't know.
Cite the sources you used with their numbers, like [1] or [2].
Answer in the same language as the question."""


def build_messages(question: str, hits: list[Hit]) -> list[Message]:
    if hits:
        context = "\n\n".join(
            f"[{n}] (source: {hit.chunk.doc_id}, chunk {hit.chunk.index})\n{hit.chunk.text}"
            for n, hit in enumerate(hits, start=1)
        )
    else:
        context = "(no relevant context found)"

    user = f"Context:\n{context}\n\nQuestion: {question}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
