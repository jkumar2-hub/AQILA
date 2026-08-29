"""
AQILA — Ingest API Router

Owner: M4 — Backend / Platform / Integration

P0 endpoints:
    POST /api/ingest/upload
    GET  /api/ingest/status/{source_id}

Pipeline:
    Upload
        ↓
    BackgroundTask
        ↓
    M1 parse_and_chunk()
        ↓
    M1 index_chunks()
        ↓
    ChromaDB
        ↓
    SQLite status = indexed
"""

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    UploadFile,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db, AsyncSessionLocal
from ..db.models import Source
from ..schemas.models import (
    IngestStatusResponse,
    IngestUploadResponse,
)


# ---------------------------------------------------------------------------
# ROUTER
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/ingest",
    tags=["ingest"],
)


# ---------------------------------------------------------------------------
# UPLOAD DIRECTORY
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------------------------
# BACKGROUND INGESTION PIPELINE
# ---------------------------------------------------------------------------

async def process_ingest(
    source_id: str,
    file_path: str,
):
    """
    Background ingestion pipeline.

    P0 document pipeline:

        parse_and_chunk()
            ↓
        index_chunks()
            ↓
        ChromaDB
            ↓
        SQLite status = indexed

    P1:

        Audio/image ingestion is currently unsupported.

    Important:
        M1 functions are synchronous/heavy, so they are executed
        using asyncio.to_thread() to avoid blocking FastAPI's
        event loop.
    """

    async with AsyncSessionLocal() as db:

        # ---------------------------------------------------------
        # Find source record
        # ---------------------------------------------------------

        result = await db.execute(
            select(Source).where(
                Source.source_id == source_id
            )
        )

        source = result.scalar_one_or_none()

        if source is None:
            print(
                f"[AQILA] Source not found: {source_id}",
                flush=True,
            )
            return

        try:

            # -----------------------------------------------------
            # Determine modality
            # -----------------------------------------------------

            modality = source.modality or "text"

            print(
                f"[AQILA] Starting ingestion: "
                f"{source.file_name} "
                f"(modality={modality})",
                flush=True,
            )

            # -----------------------------------------------------
            # P1 guard — audio/image
            # -----------------------------------------------------

            if modality in ("audio", "image"):

                raise NotImplementedError(
                    f"Ingestion for modality '{modality}' "
                    f"is not yet implemented (P1). "
                    f"Only PDF and DOCX are supported at P0."
                )

            # -----------------------------------------------------
            # Import M1 pipeline
            # -----------------------------------------------------

            from rag.parsers import parse_and_chunk
            from rag.retriever import index_chunks

            # =====================================================
            # M1 — PARSE + CHUNK
            # =====================================================

            print(
                f"[AQILA] Starting parse: "
                f"{source.file_name}",
                flush=True,
            )

            chunks = await asyncio.to_thread(
                parse_and_chunk,
                file_path=file_path,
                source_id=source_id,
                file_name=source.file_name,
                modality=modality,
            )

            print(
                f"[AQILA] Parsing complete: "
                f"{len(chunks)} chunks",
                flush=True,
            )

            # =====================================================
            # M1 — EMBED + CHROMADB INDEX
            # =====================================================

            print(
                "[AQILA] Starting ChromaDB indexing...",
                flush=True,
            )

            chunk_count = await asyncio.to_thread(
                index_chunks,
                chunks,
                source_type=source.source_type or "pdf",
                file_created_at=source.created_at,
            )

            print(
                f"[AQILA] ChromaDB indexing complete: "
                f"{chunk_count} chunks",
                flush=True,
            )

            # =====================================================
            # SQLITE — SUCCESS
            # =====================================================

            source.status = "indexed"

            source.chunk_count = chunk_count

            source.error_message = None

            await db.commit()

            print(
                f"[AQILA] Ingested "
                f"{source.file_name}: "
                f"{chunk_count} chunks",
                flush=True,
            )

        except Exception as exc:

            # =====================================================
            # SQLITE — FAILURE
            # =====================================================

            source.status = "failed"

            source.chunk_count = 0

            source.error_message = str(exc)

            await db.commit()

            print(
                f"[AQILA] Ingestion failed for "
                f"{source.file_name}: "
                f"{exc}",
                flush=True,
            )


# ---------------------------------------------------------------------------
# UPLOAD ENDPOINT
# ---------------------------------------------------------------------------

@router.post(
    "/upload",
    response_model=IngestUploadResponse,
)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a file and start background ingestion.
    """

    # ---------------------------------------------------------
    # Generate source ID
    # ---------------------------------------------------------

    source_id = str(uuid4())

    # ---------------------------------------------------------
    # Determine filename
    # ---------------------------------------------------------

    filename = file.filename or "unknown"

    # ---------------------------------------------------------
    # Determine extension
    # ---------------------------------------------------------

    extension = Path(filename).suffix.lower()

    # ---------------------------------------------------------
    # Build upload path
    # ---------------------------------------------------------

    file_path = (
        UPLOAD_DIR
        / f"{source_id}_{filename}"
    )

    # ---------------------------------------------------------
    # Save uploaded file
    # ---------------------------------------------------------

    contents = await file.read()

    file_path.write_bytes(contents)

    print(
        f"[AQILA] File uploaded: "
        f"{filename} "
        f"({len(contents)} bytes)",
        flush=True,
    )

    # ---------------------------------------------------------
    # Source type mapping
    # ---------------------------------------------------------

    source_type_map = {
        ".pdf": "pdf",
        ".docx": "docx",

        # P1 modalities
        ".wav": "audio",
        ".mp3": "audio",
        ".m4a": "audio",

        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
    }

    source_type = source_type_map.get(
        extension
    )

    # ---------------------------------------------------------
    # Modality
    # ---------------------------------------------------------

    if source_type == "audio":

        modality = "audio"

    elif source_type == "image":

        modality = "image"

    else:

        modality = "text"

    # ---------------------------------------------------------
    # Timestamp
    # ---------------------------------------------------------

    now = datetime.now(
        timezone.utc
    ).isoformat()

    # ---------------------------------------------------------
    # Create SQLite Source record
    # ---------------------------------------------------------

    source = Source(
        source_id=source_id,
        file_name=filename,
        file_path=str(file_path),
        source_type=source_type,
        modality=modality,
        status="processing",
        chunk_count=0,
        created_at=now,
    )

    db.add(source)

    await db.commit()

    print(
        f"[AQILA] Source created: "
        f"{source_id}",
        flush=True,
    )

    # ---------------------------------------------------------
    # Start background ingestion
    # ---------------------------------------------------------

    background_tasks.add_task(
        process_ingest,
        source_id,
        str(file_path),
    )

    print(
        f"[AQILA] Background ingestion queued: "
        f"{source_id}",
        flush=True,
    )

    # ---------------------------------------------------------
    # Return immediately
    # ---------------------------------------------------------

    return IngestUploadResponse(
        source_id=source_id,
        status="processing",
    )


# ---------------------------------------------------------------------------
# INGESTION STATUS ENDPOINT
# ---------------------------------------------------------------------------

@router.get(
    "/status/{source_id}",
    response_model=IngestStatusResponse,
)
async def ingest_status(
    source_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Return current ingestion status.
    """

    # ---------------------------------------------------------
    # Find source
    # ---------------------------------------------------------

    result = await db.execute(
        select(Source).where(
            Source.source_id == source_id
        )
    )

    source = result.scalar_one_or_none()

    # ---------------------------------------------------------
    # Source not found
    # ---------------------------------------------------------

    if source is None:

        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Source not found",
        )

    # ---------------------------------------------------------
    # Return status
    # ---------------------------------------------------------

    return IngestStatusResponse(
        source_id=source.source_id,
        status=source.status or "processing",
    )