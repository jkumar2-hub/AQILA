"""
rag/tests/mock_retrieval.py
────────────────────────────────────────────────────────────────────────────
AQILA — Mock RetrievalResult Fixture for M1 and M2 Development
Owner: M1 — AI / ML + RAG Core

PLACEHOLDER — M1 fills this with realistic mock data at Hour 0–2 of the hackathon.

Purpose:
  Provides a hardcoded list of RetrievalResult objects so that:
  - M1 can test its own pipeline shapes before real ChromaDB retrieval works
  - M2 can develop the pairwise cosine / graph / contradiction logic
    WITHOUT waiting for M1 to complete real retrieval

CONTRACT REQUIREMENTS (per v4.1 §4 Mock Data Strategy):
  - Each mock result must include:
      embedding: list[float]        — 384-dim random unit vector (MiniLM space)
      embedding_space: str          — "minilm"
  - This is sufficient for M2 to test pairwise cosine same-space guard
  - mock_response.json (M3 mock) must NOT include embedding or embedding_space

FROZEN FIELDS (must match docs/API_CONTRACTS.md after Hour 2):
  query, source_id, source_type, chunk_id, text, score, modality,
  page_number, timestamp_start, timestamp_end, file_name, file_created_at,
  metadata, embedding, embedding_space

References:
  - docs/API_CONTRACTS.md  — RetrievalResult full contract
"""

import random
import math

# TODO (M1, Hour 0–2): Replace this skeleton with realistic mock data.
#   Include at least 2 sources, 4 chunks, all embedding_space="minilm",
#   embedding as 384-dim unit vectors.

def _random_unit_vector(dim: int = 384) -> list:
    """Generate a random unit vector of given dimension."""
    vec = [random.gauss(0, 1) for _ in range(dim)]
    magnitude = math.sqrt(sum(x * x for x in vec))
    return [x / magnitude for x in vec]


# Skeleton — M1 must replace with realistic RetrievalResult dicts/objects
MOCK_RETRIEVAL_RESULTS: list[dict] = [
    # TODO (M1, Hour 0–2): Populate with realistic mock RetrievalResult data
    # Example shape (must match API_CONTRACTS.md exactly):
    # {
    #     "query": "Who was confirmed at the meeting?",
    #     "source_id": "<uuid>",
    #     "source_type": "pdf",
    #     "chunk_id": "<uuid>",
    #     "text": "Agent Mehra confirmed presence at Sector 7 on March 15 2024.",
    #     "score": 0.92,
    #     "modality": "text",
    #     "page_number": 1,
    #     "timestamp_start": None,
    #     "timestamp_end": None,
    #     "file_name": "field_report.pdf",
    #     "file_created_at": "2024-03-15T03:00:00Z",
    #     "metadata": {},
    #     "embedding": _random_unit_vector(384),  # 384-dim unit vector
    #     "embedding_space": "minilm",             # REQUIRED
    # },
]
