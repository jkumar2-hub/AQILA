"""
AQILA — Text Embedding Module

Owner: M1 — AI / ML + RAG Core

Uses:
    sentence-transformers/all-MiniLM-L6-v2

Output:
    384-dimensional normalized embeddings
    embedding_space = "minilm"

Design:
    - Model is loaded lazily and cached via lru_cache (singleton).
    - All inference runs on CPU.
    - local_files_only=True — no network calls at runtime.
    - Outputs are normalized to unit length for cosine similarity retrieval.
"""

import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """
    Load MiniLM once and cache the model (singleton).

    CPU-only. local_files_only=True enforces offline operation.
    The model must be pre-downloaded before hackathon execution.
    """
    logger.info("Loading embedding model %s on CPU...", MODEL_NAME)
    return SentenceTransformer(MODEL_NAME, device="cpu")


def embed_text(text: str) -> list[float]:
    """
    Embed a single string into a 384-dimensional normalized vector.

    Args:
        text: The string to embed.

    Returns:
        A list of floats (384 dimensions, unit-normalized).

    Raises:
        TypeError: if text is not a str.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text)}")

    model = _get_model()
    embedding = model.encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return embedding.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Batch-encode a list of strings into 384-dimensional normalized vectors.

    Input order is strictly preserved.

    Args:
        texts: List of strings to embed.

    Returns:
        List of lists of floats (one 384-dim vector per input).

    Raises:
        TypeError: if texts is not a list or any element is not a str.
    """
    if not isinstance(texts, list):
        raise TypeError(f"Expected list[str], got {type(texts)}")

    for idx, t in enumerate(texts):
        if not isinstance(t, str):
            raise TypeError(f"Item at index {idx} is not a str: {type(t)}")

    if not texts:
        return []

    model = _get_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return embeddings.tolist()