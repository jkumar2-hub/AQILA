"""
backend/app/schemas/
────────────────────────────────────────────────────────────────────────────
AQILA — Pydantic Request / Response Models
Owner: M4 — Backend / Platform / Integration

PLACEHOLDER — Implementation begins at Hour 0 of the hackathon.

This package will contain Pydantic models for:
  - IngestUploadRequest / IngestStatusResponse
  - QueryRequest / AQILAResponse
  - Citation, Contradiction, EvidenceGraph, GraphNode, GraphEdge
  - SourceSummary
  - SettingsStatusResponse

All models must match the frozen contracts in docs/API_CONTRACTS.md.

IMPORTANT: AQILAResponse must NOT contain embedding or embedding_space fields.
           M4 strips these from RetrievalResult before building AQILAResponse.

References:
  - docs/API_CONTRACTS.md  — canonical frozen contracts (read-only after Hour 2)
"""

# TODO (M4, Hour 0–2): Implement Pydantic schemas here
