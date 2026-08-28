"""
rag/parsers.py
──────────────────────────────────────────────────────────────────────────────
AQILA — PDF Parser and Chunker
Owner: M1 — AI / ML + RAG Core

PUBLIC API
----------
parse_pdf(file_path: str, source_id: str) -> list[dict]
    Parse a PDF file and return a list of RetrievalResult-compatible chunk
    dicts.  Each dict contains every field defined in docs/API_CONTRACTS.md
    for the RetrievalResult contract.

    Fields that only make sense after retrieval (score, embedding,
    embedding_space, query) are set to their null/zero defaults so that the
    dict is immediately contract-compliant without breaking any downstream
    consumer.

PRIMARY PARSER  : Docling  (layout-aware; CPU-only; no LLM)
FALLBACK PARSER : PyMuPDF  (reliable; used when Docling raises any exception)

Chunking strategy (per v4.1 §3 M1):
    target  ≈ 400 tokens  (approximated as whitespace-split word count × 1.3)
    overlap = 50 tokens

No network calls.  No model loading.  No CUDA required.
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Chunking constants (per v4.1 §3 M1) ─────────────────────────────────────
# Target 400 tokens
# Overlap 50 tokens
_TARGET_TOKENS: int = 400
_OVERLAP_TOKENS: int = 50


# ── Public API ───────────────────────────────────────────────────────────────

def parse_pdf(file_path: str, source_id: str) -> list[dict[str, Any]]:
    """Parse a PDF file and return a list of RetrievalResult-compatible dicts.

    Each returned dict is immediately compatible with the frozen RetrievalResult
    contract (docs/API_CONTRACTS.md).  Fields populated by later pipeline stages
    (score, embedding, embedding_space, query) are set to their null defaults.

    Parameters
    ----------
    file_path:
        Absolute or relative path to the PDF file.
    source_id:
        Caller-supplied UUID that uniquely identifies this ingestion run.

    Returns
    -------
    list[dict]
        One dict per text chunk.  Never raises on empty pages — those are
        silently skipped.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at ``file_path``.
    ValueError
        If the file does not have a ``.pdf`` extension (case-insensitive).
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a .pdf file, got '{path.suffix}' ({file_path}). "
            "DOCX / audio / image support is not yet implemented in this module."
        )

    file_name = path.name
    file_created_at = _get_file_created_at(path)

    # Try Docling first; fall back to PyMuPDF on any exception.
    try:
        pages = _extract_pages_docling(path)
        logger.debug("Docling extraction succeeded for %s", file_name)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Docling extraction failed for %s (%s). Falling back to PyMuPDF.",
            file_name,
            exc,
        )
        pages = _extract_pages_pymupdf(path)

    chunks = _chunk_pages(pages)
    return _build_records(chunks, source_id, file_name, file_created_at)


# ── Internal: page extraction ─────────────────────────────────────────────────

def _extract_pages_docling(path: Path) -> list[dict[str, Any]]:
    """Extract per-page text using Docling (primary parser).

    Returns a list of ``{"page_number": int, "text": str}`` dicts.
    Empty pages are included as empty strings; callers filter them.

    Raises any Docling exception so the caller can fall back to PyMuPDF.
    """
    # Import inside function so that a missing/broken docling install does NOT
    # crash the module at import time — it will just trigger the PyMuPDF
    # fallback when parse_pdf() is called.
    from docling.datamodel.base_models import ConversionStatus
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    # CPU-only, no OCR model download, no table extraction model download.
    # We only need the raw text; layout information (headings, tables) is a
    # bonus but not required for chunking.
    pipeline_options = PdfPipelineOptions(
        do_ocr=False,
        do_table_structure=False,
        do_picture_classification=False,
        do_picture_description=False,
        do_formula_enrichment=False,
        do_code_enrichment=False,
    )

    converter = DocumentConverter(
        format_options={
            "pdf": PdfFormatOption(pipeline_options=pipeline_options),
        }
    )

    result = converter.convert(str(path))

    if result.status not in (
        ConversionStatus.SUCCESS,
        ConversionStatus.PARTIAL_SUCCESS,
    ):
        raise RuntimeError(
            f"Docling conversion returned status {result.status} for {path.name}"
        )

    doc = result.document

    # Docling exposes pages via doc.pages; text is available via the markdown
    # export or by iterating text items.  We use the markdown export split by
    # page markers, which is robust across Docling versions.
    #
    # Docling's DoclingDocument has an .export_to_markdown() method that
    # emits page separators.  We use page-level text items instead for
    # accurate page attribution.
    pages: list[dict[str, Any]] = []

    # Docling >= 2.x: doc.pages is a dict keyed by 1-based page number.
    # Each page has a .cells attribute with text cells, or we can iterate
    # doc.texts which have .prov containing page references.
    page_texts: dict[int, list[str]] = {}

    for text_item in doc.texts:
        for prov in text_item.prov:
            page_no = prov.page_no  # 1-based
            page_texts.setdefault(page_no, []).append(text_item.text)

    # Sort pages by page number and yield them in order.
    if page_texts:
        for page_no in sorted(page_texts.keys()):
            combined = " ".join(page_texts[page_no])
            pages.append({"page_number": page_no, "text": combined})
    else:
        # Fallback within Docling: export full markdown and treat as page 1.
        md = doc.export_to_markdown()
        if md.strip():
            pages.append({"page_number": 1, "text": md})

    return pages


def _extract_pages_pymupdf(path: Path) -> list[dict[str, Any]]:
    """Extract per-page text using PyMuPDF (fallback parser).

    Returns a list of ``{"page_number": int, "text": str}`` dicts.
    Pages with no extractable text are returned with empty strings.
    """
    import pymupdf  # PyMuPDF >= 1.24 canonical import

    pages: list[dict[str, Any]] = []
    with pymupdf.open(str(path)) as doc:
        for page_index, page in enumerate(doc):
            text = page.get_text("text") or ""
            pages.append({"page_number": page_index + 1, "text": text})
    return pages


# ── Internal: chunking ────────────────────────────────────────────────────────

def _chunk_pages(
    pages: list[dict[str, Any]],
    target_tokens: int = _TARGET_TOKENS,
    overlap_tokens: int = _OVERLAP_TOKENS,
) -> list[dict[str, Any]]:
    """Split page texts into overlapping token-based chunks.

    Algorithm
    ---------
    1. Tokenize each page's text using tiktoken.
    2. Slide a window of ``target_tokens`` tokens with ``overlap_tokens`` step-back.
    3. Skip windows that produce only whitespace after decoding.
    4. Record the page_number from the page where the chunk *starts*.
    5. Assign a monotonically increasing chunk_index across all pages.

    Parameters
    ----------
    pages:
        List of ``{"page_number": int, "text": str}`` dicts.
    target_tokens:
        Target window size in tokens (400 tokens).
    overlap_tokens:
        Number of tokens repeated from the previous chunk (50 tokens).

    Returns
    -------
    list[dict]  with keys: page_number, chunk_index, text
    """
    import tiktoken
    tokenizer = tiktoken.get_encoding("cl100k_base")

    step = max(1, target_tokens - overlap_tokens)
    chunks: list[dict[str, Any]] = []
    chunk_index = 0
    carry_tokens: list[int] = []   # tokens rolled over from the previous page
    carry_page: int = 1           # page number those carry tokens belong to

    for page in pages:
        page_no: int = page["page_number"]
        raw_text: str = page["text"]
        tokens = tokenizer.encode(raw_text)

        if not tokens:
            # Empty page — skip without crashing.
            logger.debug("Skipping empty page %d", page_no)
            continue

        # Prepend overlap tokens carried from the previous page.
        if carry_tokens:
            combined_tokens = carry_tokens + tokens
            # The chunk starts logically at carry_page, but we attribute it to
            # the current page for page_number accuracy (the majority of the
            # content is on the current page unless carry is larger than step,
            # which it never is given overlap < target).
            current_page_no = page_no
        else:
            combined_tokens = tokens
            current_page_no = page_no

        pos = 0
        first_in_page = True
        while pos < len(combined_tokens):
            window = combined_tokens[pos : pos + target_tokens]
            text = tokenizer.decode(window).strip()

            if text:
                # For the first chunk of a page that uses carry tokens, set the
                # page number to the carry page (the chunk starts there).
                attributed_page = carry_page if (first_in_page and carry_tokens) else current_page_no
                chunks.append(
                    {
                        "page_number": attributed_page,
                        "chunk_index": chunk_index,
                        "text": text,
                    }
                )
                chunk_index += 1

            if pos + target_tokens >= len(combined_tokens):
                break

            pos += step
            first_in_page = False

        # Compute the carry-over: last overlap_tokens of this page's tokens
        # (not including carry-in, to avoid cascading overlap inflation).
        page_only_tokens = tokens  # excludes the prepended carry
        carry_tokens = page_only_tokens[-overlap_tokens:] if len(page_only_tokens) > overlap_tokens else page_only_tokens[:]
        carry_page = page_no

    return chunks


# ── Internal: record builder ──────────────────────────────────────────────────

def _build_records(
    chunks: list[dict[str, Any]],
    source_id: str,
    file_name: str,
    file_created_at: str | None,
) -> list[dict[str, Any]]:
    """Wrap raw chunks in RetrievalResult-compatible dicts.

    Fields set to null defaults (populated by later pipeline stages):
        query, score, embedding, embedding_space

    ``chunk_id`` is a deterministic UUID v5 derived from source_id + chunk_index,
    ensuring reproducibility across identical re-ingestions.

    ``chunk_index`` is stored in ``metadata`` (it is not a top-level
    RetrievalResult field per docs/API_CONTRACTS.md).
    """
    namespace = uuid.UUID("a01a0000-0000-0000-0000-000000000000")
    records: list[dict[str, Any]] = []

    for chunk in chunks:
        chunk_index: int = chunk["chunk_index"]
        # Deterministic chunk_id: UUID v5 of "<source_id>:<chunk_index>"
        chunk_id = str(
            uuid.uuid5(namespace, f"{source_id}:{chunk_index}")
        )

        record: dict[str, Any] = {
            # ── RetrievalResult top-level fields (docs/API_CONTRACTS.md) ──
            "query": "",                      # populated at retrieval time
            "source_id": source_id,
            "source_type": "pdf",
            "chunk_id": chunk_id,
            "text": chunk["text"],
            "score": 0.0,                     # populated after ChromaDB retrieval
            "modality": "text",
            "page_number": chunk["page_number"],
            "timestamp_start": None,
            "timestamp_end": None,
            "file_name": file_name,
            "file_created_at": file_created_at,
            "metadata": {
                "chunk_index": chunk_index,   # stored in metadata per contract
            },
            # ── Fields populated by embedder / retriever ──────────────────
            "embedding": None,
            "embedding_space": None,
        }
        records.append(record)

    return records


# ── Internal: helpers ─────────────────────────────────────────────────────────

def _get_file_created_at(path: Path) -> str | None:
    """Return the file's creation/modification time as an ISO 8601 UTC string.

    On Windows ``st_ctime`` is the creation time; on POSIX it is the last
    metadata-change time.  We take whichever is earlier between ctime and mtime
    as a best-effort creation timestamp.
    """
    try:
        stat = path.stat()
        ts = min(stat.st_ctime, stat.st_mtime)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.isoformat()
    except OSError:
        return None
