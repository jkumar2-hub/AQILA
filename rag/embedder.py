import logging

logger = logging.getLogger(__name__)

# Private singleton instance
_model = None
_MODEL_NAME = "all-MiniLM-L6-v2"


def _get_model():
    """Lazily load and return the SentenceTransformer model singleton.

    To strictly comply with offline, zero-network requirements after caching,
    this attempts to load with local_files_only=True.
    """
    global _model
    if _model is None:
        logger.info(f"Loading embedding model {_MODEL_NAME} on CPU...")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError("sentence-transformers is not installed.") from e

        try:
            # We explicitly target the CPU and prevent network calls.
            # If it is not cached, this will fail exactly as required by the spec.
            _model = SentenceTransformer(
                _MODEL_NAME, device="cpu", local_files_only=True
            )
        except Exception as e:
            raise RuntimeError(
                f"Model '{_MODEL_NAME}' not found locally, and downloads are restricted. "
                f"Please ensure it is downloaded and cached. Original error: {e}"
            ) from e

    return _model


def embed_text(text: str) -> list[float]:
    """Embed a single string into a 384-dimensional vector.

    Outputs are normalized to unit length for cosine similarity calculations.

    Args:
        text: The string to embed.

    Returns:
        A list of floats representing the embedding vector.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected a string, got {type(text)}")

    model = _get_model()
    # SentenceTransformer handles empty strings gracefully.
    # We normalize embeddings to ensure direct compatibility with cosine
    # similarity during retrieval.
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings into 384-dimensional vectors.

    Outputs are normalized to unit length for cosine similarity calculations.
    Order is strictly preserved.

    Args:
        texts: A list of strings to embed.

    Returns:
        A list of lists of floats, representing the embedding vectors.
    """
    if not isinstance(texts, list):
        raise TypeError(f"Expected a list of strings, got {type(texts)}")

    for idx, t in enumerate(texts):
        if not isinstance(t, str):
            raise TypeError(f"Item at index {idx} is not a string: {type(t)}")

    if not texts:
        return []

    model = _get_model()
    # Batch encode
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
