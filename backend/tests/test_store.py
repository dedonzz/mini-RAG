import numpy as np
import pytest

from app.rag.store import Chunk, VectorStore


def unit(*values: float) -> np.ndarray:
    v = np.array(values, dtype=np.float32)
    return v / np.linalg.norm(v)


def make_store(tmp_path=None) -> VectorStore:
    store = VectorStore(tmp_path)
    store.add(
        [Chunk("a.txt", 0, "cats"), Chunk("a.txt", 1, "dogs"), Chunk("b.txt", 0, "cars")],
        np.stack([unit(1, 0, 0), unit(0.9, 0.1, 0), unit(0, 0, 1)]),
        "fake",
    )
    return store


def test_search_returns_most_similar_first():
    hits = make_store().search(unit(1, 0, 0), top_k=2)
    assert [h.chunk.text for h in hits] == ["cats", "dogs"]
    assert hits[0].score == pytest.approx(1.0)
    assert hits[0].score > hits[1].score


def test_top_k_larger_than_store():
    assert len(make_store().search(unit(1, 0, 0), top_k=10)) == 3


def test_empty_store_returns_nothing():
    assert VectorStore().search(unit(1, 0, 0), top_k=3) == []


def test_delete_doc_removes_its_chunks_and_vectors():
    store = make_store()
    assert store.delete_doc("a.txt") == 2
    assert len(store) == 1
    assert store.vectors.shape == (1, 3)
    assert store.search(unit(1, 0, 0), top_k=1)[0].chunk.text == "cars"


def test_dimension_mismatch_is_rejected():
    store = make_store()
    with pytest.raises(ValueError):
        store.add([Chunk("c.txt", 0, "x")], np.ones((1, 5), dtype=np.float32), "fake")


def test_save_and_load_round_trip(tmp_path):
    make_store(tmp_path).save()
    loaded = VectorStore(tmp_path)
    loaded.load()
    assert loaded.embedder_name == "fake"
    assert loaded.chunk_counts() == {"a.txt": 2, "b.txt": 1}
    assert loaded.search(unit(0, 0, 1), top_k=1)[0].chunk.text == "cars"
