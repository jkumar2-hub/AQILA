"""
backend/app/db/chroma.py

AQILA — ChromaDB Client Initialisation
Owner: M4 — Backend / Platform / Integration

Provides the persistent ChromaDB client and AQILA collections.

P0:
    documents_col — 384-dim MiniLM text embeddings

P1:
    audio_col     — 384-dim MiniLM audio/transcript embeddings
    images_col    — 512-dim CLIP image embeddings
"""

import os
from pathlib import Path

import chromadb


CHROMA_PERSIST_PATH = os.getenv(
    "CHROMA_PERSIST_PATH",
    "./data/chroma",
)

# Resolve relative paths from the project working directory.
CHROMA_PERSIST_PATH = str(Path(CHROMA_PERSIST_PATH).resolve())


# Persistent local ChromaDB client.
client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)


# P0 — document chunks using MiniLM embeddings.
documents_col = client.get_or_create_collection(
    name="documents_col",
    metadata={
        "embedding_space": "minilm",
        "dimension": 384,
        "hnsw:space": "cosine",
    },
)


# P1 — audio transcript chunks using MiniLM embeddings.
audio_col = client.get_or_create_collection(
    name="audio_col",
    metadata={
        "embedding_space": "minilm",
        "dimension": 384,
        "hnsw:space": "cosine",
    },
)


# P1 — image embeddings using CLIP.
images_col = client.get_or_create_collection(
    name="images_col",
    metadata={
        "embedding_space": "clip",
        "dimension": 512,
        "hnsw:space": "cosine",
    },
)


def get_chroma_client():
    """Return the shared persistent ChromaDB client."""
    return client


def get_documents_collection():
    """Return the P0 documents collection."""
    return documents_col


def get_audio_collection():
    """Return the P1 audio collection."""
    return audio_col


def get_images_collection():
    """Return the P1 image collection."""
    return images_col