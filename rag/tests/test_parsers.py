"""
rag/tests/test_parsers.py

Unit tests for rag/parsers.py

Tests are self-contained — PDFs are synthesised in pytest tmp_path
using reportlab/fpdf2/pypdf or by writing a minimal binary PDF.
No test reads from the project root.
"""

import io
import struct
import textwrap
import zlib
from pathlib import Path

import pytest

from rag.parsers import chunk_text, parse_and_chunk


# ---------------------------------------------------------------------------
# Helpers: minimal PDF builder (no external deps)
# ---------------------------------------------------------------------------

def _write_minimal_pdf(path: Path, pages: list[str]) -> None:
    """
    Write a syntactically valid PDF containing the given page texts.
    Uses PyMuPDF (fitz) to create a real PDF so that both Docling
    and PyMuPDF parsers can read it.
    """
    import fitz  # PyMuPDF — already a project dependency

    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


# ---------------------------------------------------------------------------
# chunk_text
# ---------------------------------------------------------------------------

class TestChunkText:
    def test_empty_string_returns_empty(self):
        assert chunk_text("") == []

    def test_whitespace_only_returns_empty(self):
        assert chunk_text("   ") == []

    def test_short_text_returns_single_chunk(self):
        text = " ".join(f"word{i}" for i in range(100))
        chunks = chunk_text(text, chunk_size=400, overlap=50)
        assert len(chunks) == 1

    def test_long_text_produces_multiple_chunks(self):
        text = " ".join(f"w{i}" for i in range(1000))
        chunks = chunk_text(text, chunk_size=400, overlap=50)
        assert len(chunks) >= 2

    def test_overlap_must_be_smaller_than_chunk_size(self):
        with pytest.raises(ValueError):
            chunk_text("hello world", chunk_size=10, overlap=10)

    def test_overlap_content_shared(self):
        """Consecutive chunks share the last `overlap` words of the previous chunk."""
        overlap = 5
        chunk_size = 20
        words = [f"w{i}" for i in range(60)]
        text = " ".join(words)

        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        assert len(chunks) >= 2

        # Last `overlap` words of chunk 0 must appear at start of chunk 1.
        tail = chunks[0].split()[-overlap:]
        head = chunks[1].split()[:overlap]
        assert tail == head


# ---------------------------------------------------------------------------
# parse_and_chunk — PDF integration
# ---------------------------------------------------------------------------

class TestParseAndChunk:
    def test_single_page_pdf(self, tmp_path):
        p = tmp_path / "test.pdf"
        _write_minimal_pdf(p, ["This is page one with some content to parse."])
        results = parse_and_chunk(str(p), source_id="s1", file_name="test.pdf")
        assert len(results) >= 1

    def test_multipage_pdf(self, tmp_path):
        p = tmp_path / "multi.pdf"
        _write_minimal_pdf(p, ["Page one content.", "Page two content."])
        results = parse_and_chunk(str(p), source_id="s2", file_name="multi.pdf")
        assert len(results) >= 1

    def test_output_fields(self, tmp_path):
        p = tmp_path / "fields.pdf"
        _write_minimal_pdf(p, ["Field test content for chunk verification."])
        results = parse_and_chunk(str(p), source_id="s3", file_name="fields.pdf")
        assert results
        chunk = results[0]
        assert "source_id" in chunk
        assert chunk["source_id"] == "s3"
        assert "file_name" in chunk
        assert chunk["file_name"] == "fields.pdf"
        assert "chunk_index" in chunk
        assert "text" in chunk
        assert isinstance(chunk["text"], str)

    def test_chunk_indexes_start_at_zero(self, tmp_path):
        p = tmp_path / "index.pdf"
        _write_minimal_pdf(p, ["Indexed content for chunk ordering check."])
        results = parse_and_chunk(str(p), source_id="s4", file_name="index.pdf")
        assert results[0]["chunk_index"] == 0

    def test_chunk_indexes_are_sequential(self, tmp_path):
        p = tmp_path / "seq.pdf"
        text = " ".join(f"word{i}" for i in range(2000))
        _write_minimal_pdf(p, [text])
        results = parse_and_chunk(str(p), source_id="s5", file_name="seq.pdf")
        for i, chunk in enumerate(results):
            assert chunk["chunk_index"] == i

    def test_unsupported_extension_raises_value_error(self, tmp_path):
        p = tmp_path / "file.txt"
        p.write_text("not a pdf")
        with pytest.raises(ValueError):
            parse_and_chunk(str(p), source_id="sx", file_name="file.txt")

    def test_missing_file_raises_error(self, tmp_path):
        p = tmp_path / "missing.pdf"
        with pytest.raises((FileNotFoundError, Exception)):
            parse_and_chunk(str(p), source_id="sx", file_name="missing.pdf")
