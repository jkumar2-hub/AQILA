"""
backend/app/db/chroma.py
────────────────────────────────────────────────────────────────────────────
AQILA — ChromaDB Client Initialisation
Owner: M4 — Backend / Platform / Integration

PLACEHOLDER — Implementation begins at Hour 0 of the hackathon.

Three ChromaDB collections (per v4.1 §8 Embedding Strategy):
  documents_col  — 384-dim MiniLM text embeddings  (embedding_space="minilm")
  audio_col      — 384-dim MiniLM audio/transcript  (embedding_space="minilm") [P1]
  images_col     — 512-dim CLIP image embeddings    (embedding_space="clip")   [P1]

IMPORTANT:
  - documents_col and audio_col share the same embedding space ("minilm", 384-dim)
  - images_col uses a SEPARATE space ("clip", 512-dim) — NEVER mix dimensions
  - ChromaDB persistent path: ./data/chroma  (gitignored via data/)

References:
  - docs/DATA_SCHEMAS.md  — collection definitions and metadata fields
  - docs/DECISIONS_LOG.md — confirmed ChromaDB score conversion formula (M1 fills this)
"""

# TODO (M4, Hour 0–2): Implement ChromaDB client, collection get-or-create
