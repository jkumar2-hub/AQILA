"""
evidence/tests/mock_evidence.py
────────────────────────────────────────────────────────────────────────────
AQILA — Mock EvidenceResult Fixture for M2 Development
Owner: M2 — Evidence Intelligence

PLACEHOLDER — M2 fills this at Hour 0–2 of the hackathon.

Purpose:
  Provides a hardcoded EvidenceResult so M2 can:
  - Validate its own output shapes before real M1 retrieval is integrated
  - Give M4 a mock to use for stub responses in early development

Uses rag/tests/mock_retrieval.py as the INPUT fixture.
This file defines the expected OUTPUT shape.

Must match docs/API_CONTRACTS.md EvidenceResult contract exactly.

References:
  - docs/API_CONTRACTS.md      — EvidenceResult, EvidenceGraph, Claim, Entity, etc.
  - rag/tests/mock_retrieval.py — mock input (with embedding + embedding_space)
"""

# TODO (M2, Hour 0–2): Populate with mock EvidenceResult including:
#   - 2+ claims
#   - 1+ entities
#   - 1+ relationships
#   - 1 contradiction (March 15 vs March 25 scenario)
#   - EvidenceGraph with 2 nodes and 1 semantic edge
#   - temporal_links = []  (P1, empty list for now)

MOCK_EVIDENCE_RESULT: dict = {
    # TODO (M2, Hour 0–2): Fill in mock EvidenceResult dict
    # Shape defined in docs/API_CONTRACTS.md
}
