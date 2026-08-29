"""
backend/tests/test_query_integration.py

Integration tests for POST /api/query and GET /api/query/{query_id}/evidence.

Strategy:
    - Use FastAPI TestClient (synchronous via httpx ASGITransport).
    - Mock M1 retriever, M2 evidence engine, and M1 generator at the
      module-import level so tests run fully offline without Ollama or
      ChromaDB.
    - Use an in-memory SQLite database so tests do not pollute the real DB.

Tests:
    A. POST /api/query → full pipeline → AQILAResponse
    B. AQILAResponse contains NO embedding or embedding_space fields
    C. contradiction_found=True when evidence contains a contradiction
    D. GET /api/query/{query_id}/evidence → EvidenceGraph
    E. POST /api/query → 422 on empty query
    F. Existing /health endpoint still works
"""

import math
import random
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# ---------------------------------------------------------------------------
# Minimal in-memory DB for tests
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


class _TestBase(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Mock data helpers
# ---------------------------------------------------------------------------

def _unit_vector(dim: int = 384) -> list[float]:
    vec = [random.gauss(0, 1) for _ in range(dim)]
    mag = math.sqrt(sum(x * x for x in vec))
    return [x / mag for x in vec]


def _make_retrieval_result(
    query: str = "test query",
    source_id: str = "src-a",
    file_name: str = "report.pdf",
    text: str = "Agent Mehra was at Sector 7 on March 15, 2026.",
    page_number: int = 1,
    score: float = 0.9,
    embedding_space: str = "minilm",
):
    """Build a RetrievalResult-like object (plain dict → Pydantic)."""
    from backend.app.schemas.models import RetrievalResult

    return RetrievalResult(
        query=query,
        source_id=source_id,
        source_type="pdf",
        chunk_id=f"{source_id}:0",
        text=text,
        score=score,
        modality="text",
        page_number=page_number,
        timestamp_start=None,
        timestamp_end=None,
        file_name=file_name,
        file_created_at="2026-03-15T03:00:00Z",
        metadata={},
        embedding=_unit_vector(384),
        embedding_space=embedding_space,
    )


def _make_evidence_result(contradictions=None):
    from backend.app.schemas.models import (
        EvidenceGraph,
        EvidenceResult,
        GraphEdge,
        GraphNode,
    )

    nodes = [
        GraphNode(
            id="src-a",
            label="report.pdf",
            modality="text",
            color="#1D9E75",
            confidence=0.9,
        ),
    ]
    edges: list[GraphEdge] = []

    return EvidenceResult(
        claims=[],
        entities=[],
        relationships=[],
        temporal_links=[],
        contradictions=contradictions or [],
        graph=EvidenceGraph(nodes=nodes, edges=edges),
        source_references=["src-a"],
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """
    Provide a TestClient for the AQILA FastAPI app.

    The lifespan (init_db) is overridden to use an in-memory SQLite DB
    so tests do not touch data/aqila.db.
    """
    from contextlib import asynccontextmanager

    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.app.db.database import Base, get_db
    from backend.app.main import app

    # In-memory engine
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    TestSession = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with TestSession() as session:
            yield session

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    import asyncio
    asyncio.get_event_loop().run_until_complete(setup_db())

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# A. Full pipeline — no contradiction
# ---------------------------------------------------------------------------

def test_post_query_returns_aqila_response(client):
    """A. POST /api/query returns a valid AQILAResponse."""

    mock_results = [_make_retrieval_result()]
    mock_evidence = _make_evidence_result()

    with (
        patch(
            "backend.app.api.query._get_retriever",
            return_value=lambda q, top_k=8: mock_results,
        ),
        patch(
            "backend.app.api.query._get_evidence_engine",
            return_value=lambda r: mock_evidence,
        ),
        patch(
            "backend.app.api.query._get_generator",
            return_value=lambda query, retrieval_results: (
                "Agent Mehra confirmed presence [1].",
                [],
            ),
        ),
    ):
        resp = client.post("/api/query", json={"query": "Who was at Sector 7?"})

    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert "query_id" in data
    assert isinstance(data["answer"], str)
    assert isinstance(data["contradiction_found"], bool)
    assert data["contradiction_found"] is False
    assert data["contradiction_detail"] is None
    assert "evidence" in data
    assert "citations" in data
    assert "sources" in data
    assert isinstance(data["response_time_ms"], int)


# ---------------------------------------------------------------------------
# B. AQILAResponse contains NO embedding fields
# ---------------------------------------------------------------------------

def test_response_has_no_embedding_fields(client):
    """B. AQILAResponse must not expose embedding or embedding_space."""

    mock_results = [_make_retrieval_result()]
    mock_evidence = _make_evidence_result()

    with (
        patch(
            "backend.app.api.query._get_retriever",
            return_value=lambda q, top_k=8: mock_results,
        ),
        patch(
            "backend.app.api.query._get_evidence_engine",
            return_value=lambda r: mock_evidence,
        ),
        patch(
            "backend.app.api.query._get_generator",
            return_value=lambda query, retrieval_results: ("Some answer.", []),
        ),
    ):
        resp = client.post("/api/query", json={"query": "Any query"})

    assert resp.status_code == 200
    data = resp.json()

    def _no_embedding_keys(obj, path=""):
        """Recursively assert that no key named embedding/embedding_space exists."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                assert k not in ("embedding", "embedding_space"), (
                    f"Found forbidden field '{k}' at path '{path}.{k}'"
                )
                _no_embedding_keys(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                _no_embedding_keys(item, f"{path}[{i}]")

    _no_embedding_keys(data)


# ---------------------------------------------------------------------------
# C. contradiction_found=True when evidence contains a contradiction
# ---------------------------------------------------------------------------

def test_contradiction_found_true(client):
    """C. contradiction_found=True when M2 returns contradictions."""
    from backend.app.schemas.models import Contradiction

    contradiction = Contradiction(
        claim_a="Operation on March 15, 2026.",
        claim_b="Operation on March 25, 2026.",
        source_a="src-a",
        source_b="src-b",
        conflict_type="date",
        confidence=0.95,
    )

    mock_results = [
        _make_retrieval_result(source_id="src-a", text="Operation on March 15, 2026."),
        _make_retrieval_result(source_id="src-b", text="Operation on March 25, 2026."),
    ]
    mock_evidence = _make_evidence_result(contradictions=[contradiction])

    with (
        patch(
            "backend.app.api.query._get_retriever",
            return_value=lambda q, top_k=8: mock_results,
        ),
        patch(
            "backend.app.api.query._get_evidence_engine",
            return_value=lambda r: mock_evidence,
        ),
        patch(
            "backend.app.api.query._get_generator",
            return_value=lambda query, retrieval_results: (
                "Contradiction found between [1] and [2].",
                [],
            ),
        ),
    ):
        resp = client.post("/api/query", json={"query": "What was the operation date?"})

    assert resp.status_code == 200
    data = resp.json()

    assert data["contradiction_found"] is True
    assert data["contradiction_detail"] is not None
    detail = data["contradiction_detail"]
    assert detail["conflict_type"] == "date"
    assert detail["source_a"] == "src-a"
    assert detail["source_b"] == "src-b"


# ---------------------------------------------------------------------------
# D. GET /api/query/{query_id}/evidence
# ---------------------------------------------------------------------------

def test_get_query_evidence(client):
    """D. GET /api/query/{query_id}/evidence returns persisted EvidenceGraph."""
    from backend.app.schemas.models import EvidenceGraph, GraphEdge, GraphNode

    mock_results = [_make_retrieval_result()]

    # Evidence with one edge so persistence can be verified.
    mock_evidence_with_edge = _make_evidence_result()
    mock_evidence_with_edge.graph.edges.append(
        GraphEdge(
            source="src-a",
            target="src-b",
            edge_type="semantic",
            similarity=0.75,
            temporal_gap=None,
        )
    )

    with (
        patch(
            "backend.app.api.query._get_retriever",
            return_value=lambda q, top_k=8: mock_results,
        ),
        patch(
            "backend.app.api.query._get_evidence_engine",
            return_value=lambda r: mock_evidence_with_edge,
        ),
        patch(
            "backend.app.api.query._get_generator",
            return_value=lambda query, retrieval_results: ("Answer [1].", []),
        ),
    ):
        post_resp = client.post(
            "/api/query", json={"query": "Evidence persistence test?"}
        )

    assert post_resp.status_code == 200
    query_id = post_resp.json()["query_id"]

    # Fetch evidence
    get_resp = client.get(f"/api/query/{query_id}/evidence")
    assert get_resp.status_code == 200
    evidence = get_resp.json()

    assert "nodes" in evidence
    assert "edges" in evidence


# ---------------------------------------------------------------------------
# E. Empty query → 422
# ---------------------------------------------------------------------------

def test_empty_query_returns_422(client):
    """E. POST /api/query with blank query returns HTTP 422."""
    resp = client.post("/api/query", json={"query": ""})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# F. Existing /health endpoint still works
# ---------------------------------------------------------------------------

def test_health_endpoint(client):
    """F. /health endpoint continues to return 200."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


# ---------------------------------------------------------------------------
# G. GET evidence for unknown query_id → 404
# ---------------------------------------------------------------------------

def test_evidence_unknown_query_id(client):
    """G. GET /api/query/{query_id}/evidence for unknown id returns 404."""
    resp = client.get("/api/query/nonexistent-query-id-12345/evidence")
    assert resp.status_code == 404
