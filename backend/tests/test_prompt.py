from app.llm import TempMainLLM
from app.rag.prompt import build_messages
from app.rag.store import Chunk, Hit


def test_messages_have_system_then_user():
    messages = build_messages("What?", [])
    assert [m["role"] for m in messages] == ["system", "user"]
    assert "same language as the question" in messages[0]["content"]


def test_sources_are_numbered_with_their_origin():
    hits = [Hit(Chunk("notes.md", 3, "Alpha text"), 0.9), Hit(Chunk("cv.pdf", 0, "Beta text"), 0.5)]
    user = build_messages("Who?", hits)[1]["content"]
    assert "[1] (source: notes.md, chunk 3)\nAlpha text" in user
    assert "[2] (source: cv.pdf, chunk 0)\nBeta text" in user
    assert user.index("Alpha") < user.index("Beta")
    assert user.endswith("Question: Who?")


def test_no_hits_says_so():
    user = build_messages("Q", [])[1]["content"]
    assert "(no relevant context found)" in user


def test_temp_main_llm_echoes_prompt_and_is_not_configured():
    llm = TempMainLLM()
    messages = build_messages("Q", [])
    assert llm.configured is False
    assert llm.generate(messages) == messages[-1]["content"]
