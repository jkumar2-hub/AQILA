"""
backend/app/api/query.py
────────────────────────────────────────────────────────────────────────────
AQILA — Query API Router
Owner: M4 — Backend / Platform / Integration

PLACEHOLDER — Implementation begins at Hour 0 of the hackathon.

P0 Endpoints (must work by Hour 10):
  POST /api/query              — full RAG + evidence pipeline, returns AQILAResponse
  GET  /api/query/{id}/evidence — returns EvidenceGraph JSON

IMPORTANT: embedding and embedding_space fields must be STRIPPED from
RetrievalResult before assembling AQILAResponse. These fields must never
reach M3 (frontend).

References:
  - docs/API_CONTRACTS.md  — AQILAResponse, EvidenceGraph definitions
  - rag/retriever.py, rag/generator.py   (M1 modules)
  - evidence/                            (M2 modules)
"""

# TODO (M4, Hour 2–7): Implement query router and evidence endpoint
