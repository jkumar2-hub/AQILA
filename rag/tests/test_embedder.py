"""
rag/tests/test_embedder.py

Unit tests for rag/embedder.py

All tests run offline — they require the all-MiniLM-L6-v2 model to be
locally cached. If not cached, _get_model() raises RuntimeError as
specified in the AQILA spec.
"""

import json

import pytest

from rag.embedder import _get_model, embed_text, embed_texts


# ---------------------------------------------------------------------------
# A. Model loads
# ---------------------------------------------------------------------------

def test_model_loads_successfully():
    model = _get_model()
    assert model is not None
    assert str(model.device) == "cpu"


# ---------------------------------------------------------------------------
# B. Single text
# ---------------------------------------------------------------------------

def test_single_text():
    embedding = embed_text("AQILA local RAG test")
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert isinstance(embedding[0], float)


# ---------------------------------------------------------------------------
# C. Batch
# ---------------------------------------------------------------------------

def test_batch_texts():
    texts = ["AQILA test one", "AQILA test two"]
    embeddings = embed_texts(texts)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384
    assert isinstance(embeddings[0][0], float)


# ---------------------------------------------------------------------------
# D. Input order is preserved
# ---------------------------------------------------------------------------

def test_input_order_preserved():
    text1 = "First specific unique string."
    text2 = "Second different unique string."

    emb1 = embed_text(text1)
    emb2 = embed_text(text2)

    batch_embs = embed_texts([text1, text2])

    assert batch_embs[0] == pytest.approx(emb1, abs=1e-4)
    assert batch_embs[1] == pytest.approx(emb2, abs=1e-4)


# ---------------------------------------------------------------------------
# E. Determinism
# ---------------------------------------------------------------------------

def test_deterministic_output():
    text = "Deterministic testing"
    emb1 = embed_text(text)
    emb2 = embed_text(text)
    assert emb1 == pytest.approx(emb2, rel=1e-5)


# ---------------------------------------------------------------------------
# F. Empty string does not crash
# ---------------------------------------------------------------------------

def test_empty_string_does_not_crash():
    emb = embed_text("")
    assert len(emb) == 384


# ---------------------------------------------------------------------------
# G. Empty list returns empty list
# ---------------------------------------------------------------------------

def test_empty_list_returns_empty_list():
    assert embed_texts([]) == []


# ---------------------------------------------------------------------------
# H. Invalid input raises TypeError
# ---------------------------------------------------------------------------

def test_invalid_input_single():
    with pytest.raises(TypeError):
        embed_text(123)  # type: ignore
    with pytest.raises(TypeError):
        embed_text(None)  # type: ignore


def test_invalid_input_batch():
    with pytest.raises(TypeError):
        embed_texts("not a list")  # type: ignore
    with pytest.raises(TypeError):
        embed_texts(["valid", 123, "valid"])  # type: ignore


# ---------------------------------------------------------------------------
# I. Model singleton — not reloaded per call
# ---------------------------------------------------------------------------

def test_model_singleton():
    """Model is loaded only once — same object is returned on every call."""
    from rag.embedder import _get_model

    _ = embed_text("Warmup")
    model_a = _get_model()
    model_b = _get_model()

    assert model_a is model_b


# ---------------------------------------------------------------------------
# J. JSON serializable
# ---------------------------------------------------------------------------

def test_is_json_serializable():
    emb = embed_text("Test json")
    try:
        json.dumps(emb)
    except Exception as exc:
        pytest.fail(f"Embedding is not JSON serializable: {exc}")
