"""
evidence/claim_extractor.py
────────────────────────────────────────────────────────────────────────────
AQILA — Claim Extraction Module
Owner: M2 — Evidence Intelligence

PLACEHOLDER — Implementation begins at Hour 0 of the hackathon.

Responsibilities (per v4.1 §3 M2):
  Input:  list[RetrievalResult] — from M1 or mock_retrieval.py during development
  Output: list[Claim]

  - Extract key factual claims from each chunk's text field
  - Use LLM prompt (Ollama llama3.2:3b via M4's configured client)
  - Each Claim: text (str), source_id (str), confidence (float 0.0–1.0)
  - P1: confidence calibration (Hours 10–15)

INDEPENDENCE RULE (per v4.1 §3 M2):
  - M2 develops fully against mock_retrieval.py; does NOT wait for M1
  - M2 must NOT import rag/embedder.py — ever
  - M2 uses RetrievalResult.text for claim extraction
  - M2 uses RetrievalResult.embedding (not re-computed) for graph edges

References:
  - docs/API_CONTRACTS.md   — Claim, EvidenceResult contracts
  - rag/tests/mock_retrieval.py — mock input fixture
"""

# TODO (M2, Hour 0–5): Implement extract_claims(retrieval_results) -> list[Claim]
