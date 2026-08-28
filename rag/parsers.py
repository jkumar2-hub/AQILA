"""
rag/parsers.py
────────────────────────────────────────────────────────────────────────────
AQILA — Document Parser Module
Owner: M1 — AI / ML + RAG Core

PLACEHOLDER — Implementation begins at Hour 0 of the hackathon.

Responsibilities (per v4.1 §3 M1):
  - PDF/DOCX parsing
    Primary:  Docling (layout-aware)
    Fallback: PyMuPDF (immediate fallback if Docling fails at import or runtime)
  - Chunking: 400 tokens, 50-token overlap
  - P0: PDF ingestion
  - P1: DOCX ingestion (python-docx)
  - [P1] Audio: faster-whisper base model, CPU int8, word-level timestamps,
         ~200-word segments — implemented in Hours 10–15
  - [P1] Image: llama3.2-vision caption → text repr
         fallback: OCR / filename / EXIF metadata → text repr
         Hardware permitting. Must gracefully degrade on 16 GB RAM.

Output: list of chunk dicts with metadata:
  source_id, file_name, modality, page_number, chunk_index, text, ...
  (full schema in docs/DATA_SCHEMAS.md)

References:
  - docs/API_CONTRACTS.md  — RetrievalResult contract
  - docs/DATA_SCHEMAS.md   — chunk metadata fields
"""

# TODO (M1, Hour 0–5): Implement parse_pdf(), parse_docx(), chunk_text()
#                       Docling primary, PyMuPDF fallback
