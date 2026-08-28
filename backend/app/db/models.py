"""
backend/app/db/models.py
────────────────────────────────────────────────────────────────────────────
AQILA — SQLite / SQLAlchemy ORM Models
Owner: M4 — Backend / Platform / Integration

PLACEHOLDER — Implementation begins at Hour 0 of the hackathon.

P0 Tables (must exist by Hour 10):
  sources       — ingested file records (source_id, file_name, modality, status, ...)
  queries       — query history (query_id, query_text, response, timestamp, ...)

P1 Tables:
  evidence_edges — (P1) persisted graph edge records

Engine: Async SQLAlchemy + aiosqlite
DB file: ./data/aqila.db  (gitignored via data/)

References:
  - docs/DATA_SCHEMAS.md  — full table definitions
  - docs/API_CONTRACTS.md — source_id, query_id UUID formats
"""

# TODO (M4, Hour 0–2): Implement SQLAlchemy ORM models
