"""
evidence/contradiction.py
────────────────────────────────────────────────────────────────────────────
AQILA — Contradiction Detection Module
Owner: M2 — Evidence Intelligence

PLACEHOLDER — Implementation begins at Hour 0 of the hackathon.

Responsibilities (per v4.1 §3 M2 + §8 Contradiction Detection):

  P0 — Text-Based Two-Stage Detection (Golden Path):
    Stage 1 — Deterministic (no LLM cost):
      - Conflicting dates (same topic, different values)
      - Conflicting names for same entity
      - Conflicting locations for same event
      → Produces candidate conflict pairs

    Stage 2 — LLM verification (only on candidates):
      - "Do SOURCE A and SOURCE B make conflicting claims?
         Reply YES [claim_a] vs [claim_b] or NO."
      → Contradiction | None

    Demo target: field_report.pdf (March 15) vs field_report_b.pdf (March 25)
    Output conflict_type: "date"

  P1 — Cross-Modal Contradiction (Hours 10–15):
    - Audio vs text, image vs text conflict detection

OUTPUT:
  Contradiction | None — see docs/API_CONTRACTS.md for Contradiction contract

References:
  - docs/API_CONTRACTS.md   — Contradiction contract
  - demo_data/README.md     — expected demo contradiction scenario
  - rag/tests/mock_retrieval.py — mock input for development
"""

# TODO (M2, Hour 2–7): Implement detect_contradiction(retrieval_results) -> Contradiction | None
