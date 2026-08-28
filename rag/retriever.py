"""
rag/retriever.py
────────────────────────────────────────────────────────────────────────────
AQILA — ChromaDB Retrieval Module
Owner: M1 — AI / ML + RAG Core

PLACEHOLDER — Implementation begins at Hour 0 of the hackathon.

Responsibilities (per v4.1 §3 M1):

  P0 — Text-Only Retrieval (Golden Path, by Hour 10):
    - Embed query with MiniLM → 384-dim
    - Query documents_col with include=['embeddings']
    - Return top-8 FINAL RetrievalResult list
    - Set embedding_space = "minilm" on each result
    - Convert raw ChromaDB distance → normalised score [0,1]
      (formula confirmed and documented in docs/DECISIONS_LOG.md — M1 must test
       with known vectors in Hours 2–5; do NOT assume raw_distance ∈ [0,1])

  P1 — Multimodal Retrieval (Hours 10–15):
    - documents_col → top-5 CANDIDATES (embedding_space="minilm")
    - audio_col     → top-5 CANDIDATES (embedding_space="minilm")
    - images_col    → top-3 CANDIDATES (embedding_space="clip", CLIP text encoder)
    - Score normalisation per modality → weighted fusion → deduplicate
    - Final top-8 RetrievalResult list

OUTPUT CONTRACT (frozen at Hour 2):
  Returns list[RetrievalResult] — see docs/API_CONTRACTS.md for full definition.
  MUST include: embedding (list[float]), embedding_space (str)
  These fields are stripped by M4 before sending AQILAResponse to M3.

References:
  - docs/API_CONTRACTS.md  — RetrievalResult contract
  - docs/DECISIONS_LOG.md  — confirmed score conversion formula
"""

# TODO (M1, Hour 2–5): Implement retrieve_text_p0() and retrieve_multimodal_p1()
