import pytest
import json
from rag.embedder import embed_text, embed_texts, _get_model

def test_model_loads_successfully():
    """A. Model loads successfully."""
    model = _get_model()
    assert model is not None
    # Model should be on CPU
    assert str(model.device) == "cpu"

def test_single_text():
    """B. Single text embedding check."""
    embedding = embed_text("AQILA local RAG test")
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert isinstance(embedding[0], float)

def test_batch_texts():
    """C. Batch text embedding check."""
    texts = ["AQILA test one", "AQILA test two"]
    embeddings = embed_texts(texts)
    assert isinstance(embeddings, list)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384
    assert isinstance(embeddings[0][0], float)

def test_input_order_preserved():
    """D. Input order is preserved."""
    text1 = "First specific unique string."
    text2 = "Second different unique string."
    
    emb1 = embed_text(text1)
    emb2 = embed_text(text2)
    
    batch_embs = embed_texts([text1, text2])
    
    assert batch_embs[0] == pytest.approx(emb1, abs=1e-4)
    assert batch_embs[1] == pytest.approx(emb2, abs=1e-4)
    
def test_deterministic_output():
    """E. Same input produces deterministic/stable embedding values."""
    text = "Deterministic testing"
    emb1 = embed_text(text)
    emb2 = embed_text(text)
    
    assert emb1 == pytest.approx(emb2, rel=1e-5)

def test_empty_string_does_not_crash():
    """F. Empty string does not crash."""
    emb = embed_text("")
    assert len(emb) == 384

def test_empty_list_returns_empty_list():
    """G. Empty list returns an empty list."""
    embs = embed_texts([])
    assert embs == []

def test_invalid_input_single():
    """H. Invalid input raises a clear TypeError or ValueError."""
    with pytest.raises(TypeError):
        embed_text(123) # type: ignore
    with pytest.raises(TypeError):
        embed_text(None) # type: ignore

def test_invalid_input_batch():
    with pytest.raises(TypeError):
        embed_texts("not a list") # type: ignore
    with pytest.raises(TypeError):
        embed_texts(["valid", 123, "valid"]) # type: ignore

def test_is_json_serializable():
    """J. All returned values are plain Python floats/lists and can be serialized."""
    emb = embed_text("Test json")
    try:
        json.dumps(emb)
    except Exception as e:
        pytest.fail(f"Embedding is not JSON serializable: {e}")

def test_model_singleton():
    """I. Model is not unnecessarily reloaded for every call."""
    import rag.embedder
    
    # We call embed_text directly, this uses _get_model inside
    _ = embed_text("Warmup")
    
    # Ensure it's stored in the global singleton
    assert rag.embedder._model is not None
    original_model = rag.embedder._model
    
    _ = embed_text("Second call")
    # It must be the exact same object
    assert rag.embedder._model is original_model
