"""
AQILA — SQLite ORM Models
Owner: M4 — Backend / Platform / Integration
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Source(Base):
    """
    P0: Tracks all ingested source files.
    """

    __tablename__ = "sources"

    source_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    file_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    file_path: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    source_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    modality: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    status: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    chunk_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    file_created_at: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )


class Query(Base):
    """
    P0: Stores user queries and generated responses.
    """

    __tablename__ = "queries"

    query_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    query_text: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    answer: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    response_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    contradiction_found: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )


class EvidenceEdge(Base):
    """
    P1: Persisted graph edge records for past queries.
    """

    __tablename__ = "evidence_edges"

    edge_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    query_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    source_a: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    source_b: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    edge_type: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    similarity: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    temporal_gap: Mapped[float | None] = mapped_column(
        nullable=True,
    )