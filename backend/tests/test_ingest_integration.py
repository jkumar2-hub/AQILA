"""
backend/tests/test_ingest_integration.py

Integration tests for POST /api/ingest/upload and process_ingest().

Strategy:
    - Use FastAPI TestClient with an in-memory SQLite database.
    - Mock M1 (parse_and_chunk, index_chunks) so tests run fully offline
      without Docling, PyMuPDF, or ChromaDB.
    - A minimal real-ish PDF is written to tmp_path for the upload body.

Tests:
    A. Upload a PDF → response status = "processing"
    B. process_ingest() → status becomes "indexed", chunk_count > 0
    C. process_ingest() with indexing failure → status = "failed", chunk_count = 0
    D. process_ingest() for unsupported modality → status = "failed"
    E. GET /api/ingest/status/{source_id} returns current status
    F. GET /api/ingest/status/{unknown_id} → 404
"""

import asyncio
import io
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.db.database import Base, get_db
from backend.app.main import app


# ---------------------------------------------------------------------------
# In-memory DB fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    TestSession = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with TestSession() as session:
            yield session

    async def setup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.get_event_loop().run_until_complete(setup())
    app.dependency_overrides[get_db] = override_get_db

    # Also patch AsyncSessionLocal used inside process_ingest()
    with patch(
        "backend.app.api.ingest.AsyncSessionLocal",
        new=TestSession,
    ):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c, TestSession

    app.dependency_overrides.clear()


def _make_pdf_bytes() -> bytes:
    """
    Return a minimal but valid single-page PDF as bytes.
    Created without any external library.
    """
    content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 44>>
stream
BT /F1 12 Tf 100 700 Td (AQILA test document.) Tj ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
0000000368 00000 n 
trailer<</Size 6/Root 1 0 R>>
startxref
451
%%EOF"""
    return content


# ---------------------------------------------------------------------------
# A. Upload returns "processing"
# ---------------------------------------------------------------------------

def test_upload_returns_processing(client):
    c, _ = client
    resp = c.post(
        "/api/ingest/upload",
        files={"file": ("test.pdf", _make_pdf_bytes(), "application/pdf")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "processing"
    assert "source_id" in data


# ---------------------------------------------------------------------------
# B. process_ingest → indexed with chunk_count > 0
# ---------------------------------------------------------------------------

def test_process_ingest_success(client):
    """
    After process_ingest() completes with mocked M1, Source should be
    status='indexed' and chunk_count > 0.
    """
    c, TestSession = client

    # First upload to get a source_id
    resp = c.post(
        "/api/ingest/upload",
        files={"file": ("report.pdf", _make_pdf_bytes(), "application/pdf")},
    )
    assert resp.status_code == 200
    source_id = resp.json()["source_id"]

    # Run process_ingest() directly with mocked M1
    mock_chunks = [
        {
            "source_id": source_id,
            "file_name": "report.pdf",
            "modality": "text",
            "page_number": 1,
            "chunk_index": i,
            "text": f"Chunk {i} content for source {source_id}",
        }
        for i in range(3)
    ]

    with (
        patch("rag.parsers.parse_and_chunk", return_value=mock_chunks),
        patch("rag.retriever.index_chunks", return_value=3),
        patch(
            "backend.app.api.ingest.AsyncSessionLocal",
            new=TestSession,
        ),
    ):
        from backend.app.api.ingest import process_ingest
        # Determine file_path from what was saved
        from pathlib import Path
        from backend.app.api.ingest import UPLOAD_DIR

        # Find the uploaded file
        uploaded = list(UPLOAD_DIR.glob(f"{source_id}_*.pdf"))
        assert uploaded, "Uploaded file not found on disk"
        file_path = str(uploaded[0])

        asyncio.get_event_loop().run_until_complete(
            process_ingest(source_id, file_path)
        )

    # Verify DB state
    async def check():
        async with TestSession() as session:
            from backend.app.db.models import Source
            src = await session.get(Source, source_id)
            return src

    src = asyncio.get_event_loop().run_until_complete(check())
    assert src is not None
    assert src.status == "indexed"
    assert src.chunk_count == 3
    assert src.error_message is None


# ---------------------------------------------------------------------------
# C. Indexing exception → status = "failed", chunk_count = 0
# ---------------------------------------------------------------------------

def test_process_ingest_indexing_failure(client):
    """
    If index_chunks() raises an exception, Source must be:
        status = "failed"
        chunk_count = 0
        error_message != None
    """
    c, TestSession = client

    resp = c.post(
        "/api/ingest/upload",
        files={"file": ("broken.pdf", _make_pdf_bytes(), "application/pdf")},
    )
    source_id = resp.json()["source_id"]

    from backend.app.api.ingest import UPLOAD_DIR
    uploaded = list(UPLOAD_DIR.glob(f"{source_id}_*.pdf"))
    file_path = str(uploaded[0]) if uploaded else f"/tmp/{source_id}.pdf"

    mock_chunks = [{"source_id": source_id, "file_name": "broken.pdf",
                    "modality": "text", "page_number": 1,
                    "chunk_index": 0, "text": "Some text"}]

    with (
        patch("rag.parsers.parse_and_chunk", return_value=mock_chunks),
        patch("rag.retriever.index_chunks", side_effect=RuntimeError("ChromaDB connection failed")),
        patch("backend.app.api.ingest.AsyncSessionLocal", new=TestSession),
    ):
        from backend.app.api.ingest import process_ingest
        asyncio.get_event_loop().run_until_complete(
            process_ingest(source_id, file_path)
        )

    async def check():
        async with TestSession() as session:
            from backend.app.db.models import Source
            return await session.get(Source, source_id)

    src = asyncio.get_event_loop().run_until_complete(check())
    assert src.status == "failed"
    assert src.chunk_count == 0
    assert src.error_message is not None
    assert "ChromaDB" in src.error_message


# ---------------------------------------------------------------------------
# D. Unsupported modality → status = "failed" with clear message
# ---------------------------------------------------------------------------

def test_process_ingest_unsupported_modality(client):
    """
    Audio/image uploads must fail with a descriptive error,
    not crash silently or be marked as indexed.
    """
    c, TestSession = client

    # Simulate an MP3 upload
    resp = c.post(
        "/api/ingest/upload",
        files={"file": ("audio.mp3", b"FAKE_MP3_DATA", "audio/mpeg")},
    )
    assert resp.status_code == 200
    source_id = resp.json()["source_id"]

    from backend.app.api.ingest import UPLOAD_DIR
    uploaded = list(UPLOAD_DIR.glob(f"{source_id}_*.mp3"))
    file_path = str(uploaded[0]) if uploaded else f"/tmp/{source_id}.mp3"

    with patch("backend.app.api.ingest.AsyncSessionLocal", new=TestSession):
        from backend.app.api.ingest import process_ingest
        asyncio.get_event_loop().run_until_complete(
            process_ingest(source_id, file_path)
        )

    async def check():
        async with TestSession() as session:
            from backend.app.db.models import Source
            return await session.get(Source, source_id)

    src = asyncio.get_event_loop().run_until_complete(check())
    assert src.status == "failed"
    assert src.chunk_count == 0
    assert "P1" in (src.error_message or "") or "not yet" in (src.error_message or "")


# ---------------------------------------------------------------------------
# E. GET /api/ingest/status/{source_id} returns current status
# ---------------------------------------------------------------------------

def test_get_ingest_status(client):
    c, _ = client

    resp = c.post(
        "/api/ingest/upload",
        files={"file": ("check.pdf", _make_pdf_bytes(), "application/pdf")},
    )
    assert resp.status_code == 200
    source_id = resp.json()["source_id"]

    status_resp = c.get(f"/api/ingest/status/{source_id}")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["source_id"] == source_id
    assert data["status"] in ("processing", "indexed", "failed")


# ---------------------------------------------------------------------------
# F. Unknown source_id → 404
# ---------------------------------------------------------------------------

def test_get_ingest_status_unknown(client):
    c, _ = client
    resp = c.get(f"/api/ingest/status/nonexistent-source-id-99999")
    assert resp.status_code == 404
