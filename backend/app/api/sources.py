"""
AQILA — Sources API Router

Owner: M4 — Backend / Platform / Integration

P1 endpoints:
    GET    /api/sources
    DELETE /api/sources/{source_id}
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..db.models import Source


router = APIRouter(
    prefix="/api/sources",
    tags=["sources"],
)


@router.get("")
async def list_sources(
    db: AsyncSession = Depends(get_db),
):
    """
    List all ingested sources.
    """

    result = await db.execute(
        select(Source).order_by(Source.created_at.desc())
    )

    sources = result.scalars().all()

    return [
        {
            "source_id": source.source_id,
            "file_name": source.file_name,
            "source_type": source.source_type,
            "modality": source.modality,
            "status": source.status,
            "chunk_count": source.chunk_count or 0,
            "file_created_at": source.file_created_at,
            "created_at": source.created_at,
        }
        for source in sources
    ]


@router.delete("/{source_id}")
async def delete_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a source record.

    ChromaDB chunk deletion will be integrated with the
    M1 retrieval/indexing layer.
    """

    result = await db.execute(
        select(Source).where(Source.source_id == source_id)
    )

    source = result.scalar_one_or_none()

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Source not found",
        )

    await db.execute(
        delete(Source).where(Source.source_id == source_id)
    )

    await db.commit()

    return {
        "source_id": source_id,
        "status": "deleted",
    }