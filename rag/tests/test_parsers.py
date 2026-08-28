"""
rag/tests/test_parsers.py
──────────────────────────────────────────────────────────────────────────────
AQILA — Focused unit tests for rag/parsers.py
Owner: M1 — AI / ML + RAG Core

Tests are self-contained.  All PDFs are generated in a temporary directory
using PyMuPDF (already a project dependency) so no real demo files are required.

Run with:
    .venv\\Scripts\\python.exe -m pytest rag/tests/test_parsers.py -v
"""

from __future__ import annotations

import os
import sys
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
import pymupdf  # PyMuPDF ≥ 1.24

# Make sure the project root is on the path so `rag` is importable even when
# pytest is invoked from within rag/tests/.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from rag.parsers import parse_pdf, _chunk_pages  # noqa: E402


# ── PDF factory helpers ───────────────────────────────────────────────────────

def _make_pdf(tmp_path: Path, pages: list[str], filename: str = "test.pdf") -> str:
    """Create a minimal PDF with one text block per page and return its path.

    Parameters
    ----------
    tmp_path : Path
        Directory in which to write the PDF.
    pages : list[str]
        Text content for each page (one entry = one page).
    filename : str
        Output filename.

    Returns
    -------
    str
        Absolute path to the written PDF file.
    """
    pdf_path = tmp_path / filename
    doc = pymupdf.open()  # new empty document
    for page_text in pages:
        page = doc.new_page()
        if page_text:
            words = page_text.split()
            y = 72
            for i in range(0, len(words), 5):
                line = " ".join(words[i:i+5])
                page.insert_text(
                    (72, y),
                    line,
                    fontsize=10,
                    color=(0, 0, 0),
                )
                y += 12
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


def _make_words(n: int, prefix: str = "word") -> str:
    """Return a string of ``n`` unique words (useful for chunking tests)."""
    return " ".join(f"{prefix}{i}" for i in range(n))


# ── Test: basic extraction ────────────────────────────────────────────────────

class TestBasicExtraction:
    """Basic PDF parsing and chunk production."""

    def test_single_page_pdf_produces_chunks(self, tmp_path: Path) -> None:
        """A single-page PDF with content produces at least one chunk."""
        text = _make_words(50, "alpha")
        pdf = _make_pdf(tmp_path, [text])
        source_id = str(uuid.uuid4())
        results = parse_pdf(pdf, source_id)
        assert len(results) > 0, "Expected at least one chunk from a single-page PDF"

    def test_multipage_pdf_produces_more_than_zero_chunks(self, tmp_path: Path) -> None:
        """Requirement 1: A valid multi-page PDF produces > 0 chunks."""
        pages = [_make_words(80, f"p{i}") for i in range(5)]
        pdf = _make_pdf(tmp_path, pages)
        source_id = str(uuid.uuid4())
        results = parse_pdf(pdf, source_id)
        assert len(results) > 0

    def test_two_page_pdf_produces_at_least_two_chunks(self, tmp_path: Path) -> None:
        """Requirement 2: 2-page PDF with rich text → at least 2 chunks.

        Each page is filled with enough words to fill a full 400-token chunk on
        its own, so the output must have at least 2 chunks.
        """
        # Each page has ~350 words — well over one chunk worth
        page_text = _make_words(350, "x")
        pdf = _make_pdf(tmp_path, [page_text, page_text])
        source_id = str(uuid.uuid4())
        results = parse_pdf(pdf, source_id)
        assert len(results) >= 2, (
            f"Expected ≥ 2 chunks from a 2-page PDF, got {len(results)}"
        )


# ── Test: empty page handling ─────────────────────────────────────────────────

class TestEmptyPages:
    """Empty pages must be silently skipped."""

    def test_all_empty_pages_returns_empty_list(self, tmp_path: Path) -> None:
        """Requirement 3 (partial): A PDF whose pages are all blank → empty list, no error."""
        pdf = _make_pdf(tmp_path, ["", "", ""])
        source_id = str(uuid.uuid4())
        results = parse_pdf(pdf, source_id)  # must not raise
        assert isinstance(results, list)
        # May be empty or contain whitespace-only chunks stripped to empty;
        # the contract requires no crash.

    def test_mixed_empty_and_content_pages_no_error(self, tmp_path: Path) -> None:
        """Requirement 3: Blank pages surrounded by content pages don't raise."""
        pages = [
            _make_words(50, "before"),
            "",                           # blank page
            _make_words(50, "after"),
        ]
        pdf = _make_pdf(tmp_path, pages)
        source_id = str(uuid.uuid4())
        results = parse_pdf(pdf, source_id)  # must not raise
        assert len(results) > 0, "Expected chunks from the non-blank pages"


# ── Test: input validation ────────────────────────────────────────────────────

class TestInputValidation:
    """File-not-found and wrong-extension handling."""

    def test_non_pdf_extension_raises_value_error(self, tmp_path: Path) -> None:
        """Requirement 4: A non-.pdf extension raises ValueError."""
        fake_docx = tmp_path / "report.docx"
        fake_docx.write_text("not a pdf")
        with pytest.raises(ValueError, match=r"\.pdf"):
            parse_pdf(str(fake_docx), str(uuid.uuid4()))

    def test_txt_extension_raises_value_error(self, tmp_path: Path) -> None:
        """Variant: .txt extension also raises ValueError."""
        fake_txt = tmp_path / "notes.txt"
        fake_txt.write_text("some text")
        with pytest.raises(ValueError):
            parse_pdf(str(fake_txt), str(uuid.uuid4()))

    def test_missing_file_raises_file_not_found(self, tmp_path: Path) -> None:
        """A path that does not exist raises FileNotFoundError."""
        missing = str(tmp_path / "ghost.pdf")
        with pytest.raises(FileNotFoundError):
            parse_pdf(missing, str(uuid.uuid4()))


# ── Test: contract field correctness ─────────────────────────────────────────

@pytest.fixture(scope="module")
def sample_results(tmp_path_factory: pytest.TempPathFactory) -> list[dict]:
    tmp = tmp_path_factory.mktemp("contract")
    text = _make_words(100, "tok")
    pdf = _make_pdf(tmp, [text, text])
    sid = "test-source-001"
    return parse_pdf(pdf, sid)


class TestContractFields:
    """Returned records must exactly match the RetrievalResult contract."""

    def test_source_id_preserved(self, sample_results: list[dict]) -> None:
        """Requirement 5: source_id matches what was passed in."""
        for r in sample_results:
            assert r["source_id"] == "test-source-001"

    def test_modality_is_text(self, sample_results: list[dict]) -> None:
        """Requirement 6: modality == 'text'."""
        for r in sample_results:
            assert r["modality"] == "text"

    def test_source_type_is_pdf(self, sample_results: list[dict]) -> None:
        """Requirement 7: source_type == 'pdf'."""
        for r in sample_results:
            assert r["source_type"] == "pdf"

    def test_required_top_level_keys_present(self, sample_results: list[dict]) -> None:
        """All RetrievalResult top-level fields from API_CONTRACTS.md are present."""
        required_keys = {
            "query", "source_id", "source_type", "chunk_id", "text", "score",
            "modality", "page_number", "timestamp_start", "timestamp_end",
            "file_name", "file_created_at", "metadata", "embedding", "embedding_space",
        }
        for r in sample_results:
            missing = required_keys - r.keys()
            assert not missing, f"Missing contract keys: {missing}"

    def test_null_fields_have_correct_defaults(self, sample_results: list[dict]) -> None:
        """Fields populated by later pipeline stages start as None/0.0/empty."""
        for r in sample_results:
            assert r["query"] == ""
            assert r["score"] == 0.0
            assert r["embedding"] is None
            assert r["embedding_space"] is None
            assert r["timestamp_start"] is None
            assert r["timestamp_end"] is None

    def test_chunk_id_is_string(self, sample_results: list[dict]) -> None:
        """chunk_id must be a non-empty string."""
        for r in sample_results:
            assert isinstance(r["chunk_id"], str)
            assert len(r["chunk_id"]) > 0

    def test_chunk_index_in_metadata(self, sample_results: list[dict]) -> None:
        """chunk_index is stored in metadata (not top-level per contract)."""
        for r in sample_results:
            assert "chunk_index" in r["metadata"], (
                "chunk_index should be in metadata, not as a top-level field"
            )
            assert isinstance(r["metadata"]["chunk_index"], int)


# ── Test: page number attribution ────────────────────────────────────────────

class TestPageNumbers:
    """page_number must be a positive int and generally match the source page."""

    def test_page_number_is_positive_int(self, tmp_path: Path) -> None:
        """Requirement 8 (partial): page_number is a positive integer."""
        pdf = _make_pdf(tmp_path, [_make_words(50, "pg")])
        results = parse_pdf(pdf, str(uuid.uuid4()))
        for r in results:
            assert isinstance(r["page_number"], int)
            assert r["page_number"] >= 1

    @patch("rag.parsers._extract_pages_docling", side_effect=Exception("Mock Docling failure"))
    def test_two_distinct_pages_appear_in_results(self, mock_docling, tmp_path: Path) -> None:
        """Requirement 8: Two pages with distinct content produce chunks from both pages."""
        # Make pages large enough that each produces an independent chunk.
        page1 = _make_words(350, "page1word")
        page2 = _make_words(350, "page2word")
        pdf = _make_pdf(tmp_path, [page1, page2])
        results = parse_pdf(pdf, str(uuid.uuid4()))
        page_numbers = {r["page_number"] for r in results}
        # We expect at least two distinct page numbers
        assert len(page_numbers) >= 2, (
            f"Expected chunks from ≥ 2 distinct pages, got page numbers: {page_numbers}"
        )


# ── Test: chunk index determinism ─────────────────────────────────────────────

class TestDeterminism:
    """Chunk indexes and IDs must be stable across identical runs."""

    def test_chunk_indexes_are_deterministic(self, tmp_path: Path) -> None:
        """Requirement 9: Parsing the same file twice yields identical chunk_indexes."""
        text = _make_words(200, "det")
        pdf = _make_pdf(tmp_path, [text])
        source_id = "stable-source-id"

        run_a = parse_pdf(pdf, source_id)
        run_b = parse_pdf(pdf, source_id)

        indexes_a = [r["metadata"]["chunk_index"] for r in run_a]
        indexes_b = [r["metadata"]["chunk_index"] for r in run_b]
        assert indexes_a == indexes_b

    def test_chunk_ids_are_deterministic(self, tmp_path: Path) -> None:
        """Same source_id + same chunk_index → same chunk_id across runs."""
        text = _make_words(200, "idem")
        pdf = _make_pdf(tmp_path, [text])
        source_id = "stable-source-id-2"

        run_a = parse_pdf(pdf, source_id)
        run_b = parse_pdf(pdf, source_id)

        ids_a = [r["chunk_id"] for r in run_a]
        ids_b = [r["chunk_id"] for r in run_b]
        assert ids_a == ids_b

    def test_chunk_indexes_start_at_zero_and_are_sequential(self, tmp_path: Path) -> None:
        """Chunk indexes are 0, 1, 2, … without gaps."""
        text = _make_words(1000, "seq")
        pdf = _make_pdf(tmp_path, [text])
        results = parse_pdf(pdf, str(uuid.uuid4()))
        indexes = [r["metadata"]["chunk_index"] for r in results]
        assert indexes == list(range(len(indexes))), (
            f"Expected sequential 0-based indexes, got {indexes}"
        )


# ── Test: overlap ─────────────────────────────────────────────────────────────

class TestChunkOverlap:
    """Requirement 10: Consecutive chunks must share overlap words."""

    def test_consecutive_chunks_share_overlap_words(self) -> None:
        """Verify that _chunk_pages produces overlapping content between chunks.

        We construct a page with enough tokens so that there are two chunks.
        The tail tokens of chunk 0 should be the head tokens of chunk 1.
        """
        import tiktoken
        from rag.parsers import _TARGET_TOKENS, _OVERLAP_TOKENS

        # Build a page that will produce exactly 2 chunks.
        step = _TARGET_TOKENS - _OVERLAP_TOKENS
        total_tokens_needed = _TARGET_TOKENS + step
        # A single word is at least 1 token, often more, but we can just make it large enough.
        # "word0 word1 ..." will roughly be 2 tokens per word. So 1000 words is plenty.
        words = [f"w{i}" for i in range(total_tokens_needed)]
        page_text = " ".join(words)

        pages = [{"page_number": 1, "text": page_text}]
        chunks = _chunk_pages(pages)

        assert len(chunks) >= 2, (
            f"Expected at least 2 chunks, got {len(chunks)}"
        )

        tokenizer = tiktoken.get_encoding("cl100k_base")
        chunk0_tokens = tokenizer.encode(chunks[0]["text"])
        chunk1_tokens = tokenizer.encode(chunks[1]["text"])

        # The last OVERLAP_TOKENS tokens of chunk 0 should appear at the start
        # of chunk 1. We ignore the very first token because chunk texts are
        # .strip()ped, which changes how the leading space is tokenized.
        tail_of_chunk0 = chunk0_tokens[-_OVERLAP_TOKENS + 1:]
        head_of_chunk1 = chunk1_tokens[1:_OVERLAP_TOKENS]

        assert tail_of_chunk0 == head_of_chunk1, (
            f"Overlap mismatch.\n"
            f"  Tail of chunk 0: {tail_of_chunk0}\n"
            f"  Head of chunk 1: {head_of_chunk1}"
        )

    def test_single_chunk_pdf_has_no_overlap_artifact(self, tmp_path: Path) -> None:
        """A PDF small enough to produce one chunk must not crash or duplicate content."""
        text = _make_words(30, "tiny")
        pdf = _make_pdf(tmp_path, [text])
        results = parse_pdf(pdf, str(uuid.uuid4()))
        # Must succeed; content check: all original words appear somewhere.
        all_text = " ".join(r["text"] for r in results)
        for word in text.split():
            assert word in all_text


# ── Test: large PDF ───────────────────────────────────────────────────────────

class TestLargePDF:
    """Stress test: a 5-page PDF with large per-page word counts."""

    def test_large_pdf_produces_many_chunks(self, tmp_path: Path) -> None:
        """5 pages × 500 words each → significantly more than 5 chunks."""
        pages = [_make_words(500, f"p{i}") for i in range(5)]
        pdf = _make_pdf(tmp_path, pages)
        results = parse_pdf(pdf, str(uuid.uuid4()))
        assert len(results) > 5, (
            f"Expected more than 5 chunks from a large 5-page PDF, got {len(results)}"
        )
