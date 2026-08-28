"""
rag/embedder.py
────────────────────────────────────────────────────────────────────────────
AQILA — Text Embedding Module
Owner: M1 — AI / ML + RAG Core

PLACEHOLDER — Implementation begins at Hour 0 of the hackathon.

PUBLIC API (M4 calls this; M2 must NOT import this module directly):
  embed_texts(texts: list[str]) -> list[list[float]]

Responsibilities (per v4.1 §3 M1):
  - Model: sentence-transformers all-MiniLM-L6-v2 (384-dim)
  - Singleton pattern — model loaded once and cached
  - embedding_space = "minilm" for all outputs
  - Must be pre-downloaded before hackathon (no runtime model downloads)

IMPORTANT CONTRACT RULE:
  M2 (evidence/) must NOT import this module.
  M2 reads embeddings exclusively from RetrievalResult.embedding
  (populated by M1 from ChromaDB retrieval via include=['embeddings']).
  This module is called only by M4's ingest and query pipelines.

Pre-download verification command (run before hackathon):
  python -c "from sentence_transformers import SentenceTransformer;
             SentenceTransformer('all-MiniLM-L6-v2')"

References:
  - docs/API_CONTRACTS.md  — RetrievalResult.embedding, embedding_space
  - docs/DECISIONS_LOG.md  — score conversion formula (M1 documents after testing)
"""

# TODO (M1, Hour 0–2): Implement embed_texts() singleton with MiniLM
