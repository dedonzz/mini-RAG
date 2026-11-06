import pytest

from app.rag.chunker import chunk_text


def test_empty_text_gives_no_chunks():
    assert chunk_text("   \n\n  ") == []


def test_short_text_is_one_chunk():
    assert chunk_text("Hello world.", size=100, overlap=10) == ["Hello world."]


def test_chunks_respect_size():
    text = "這是一個句子。" * 200
    chunks = chunk_text(text, size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_does_not_cut_sentences_when_possible():
    sentences = [f"Sentence number {i} is here. " for i in range(30)]
    chunks = chunk_text("".join(sentences), size=120, overlap=0)
    for chunk in chunks:
        assert chunk.endswith(".")
        assert chunk.startswith("Sentence")


def test_overlap_repeats_end_of_previous_chunk():
    text = "".join(f"第{i}句。" for i in range(100))
    chunks = chunk_text(text, size=50, overlap=15)
    for prev, nxt in zip(chunks, chunks[1:]):
        # Some whole sentences (≤ 15 chars) from the end of prev start nxt.
        shared = max(n for n in range(len(nxt) + 1) if prev.endswith(nxt[:n]))
        assert 0 < shared <= 15
        assert nxt[:shared].endswith("。")


def test_no_overlap_means_no_repeated_text():
    text = "".join(f"第{i}句。" for i in range(100))
    chunks = chunk_text(text, size=50, overlap=0)
    assert "".join(chunks) == text


def test_very_long_sentence_is_hard_split():
    chunks = chunk_text("a" * 1000, size=300, overlap=0)
    assert [len(c) for c in chunks] == [300, 300, 300, 100]


def test_all_text_is_covered():
    text = "".join(f"Line {i}\n" for i in range(200))
    chunks = chunk_text(text, size=80, overlap=20)
    joined = "\n".join(chunks)
    for i in range(200):
        assert f"Line {i}" in joined


@pytest.mark.parametrize("size,overlap", [(0, 0), (100, 100), (100, -1)])
def test_invalid_parameters(size, overlap):
    with pytest.raises(ValueError):
        chunk_text("text", size=size, overlap=overlap)
