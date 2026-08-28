"""
AQILA — Async SQLite Database Configuration
Owner: M4 — Backend / Platform / Integration
"""

from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

# Project root = AQILA/
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Persistent database location
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR / 'aqila.db'}"


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """
    FastAPI dependency that provides an async database session.
    """

    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """
    Create all database tables if they do not already exist.
    """

    # Import models here so SQLAlchemy knows about them
    from . import models  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)