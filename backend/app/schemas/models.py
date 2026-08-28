"""
AQILA — Pydantic API Schemas

Owner: M4 — Backend / Platform / Integration

Source of truth:
    docs/API_CONTRACTS.md

These models define the data exchanged between:
    M1 → M2/M4
    M2 → M4
    M4 → M3
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared type aliases
# ---------------------------------------------------------------------------

SourceType = Literal["pdf", "docx", "audio", "image"]
Modality = Literal["text", "audio", "image"]
EmbeddingSpace = Literal["minilm", "clip"]
EdgeType = Literal["semantic", "temporal", "both"]
ConflictType = Literal["date", "name", "location", "fact"]


# ---------------------------------------------------------------------------
# M1 → M2 / M4
# ---------------------------------------------------------------------------

class RetrievalResult(BaseModel):
    """
    Retrieval result produced by M1.

    M1 may include the chunk embedding so M2 can construct
    pairwise semantic evidence edges.

    M4 must strip embedding and embedding_space before
    returning AQILAResponse to M3.
    """

    query: str
    source_id: str
    source_type: SourceType
    chunk_id: str
    text: str
    score: float = Field(ge=0.0, le=1.0)

    modality: Modality

    page_number: int | None = None
    timestamp_start: float | None = None
    timestamp_end: float | None = None

    file_name: str
    file_created_at: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    embedding: list[float] | None = None
    embedding_space: EmbeddingSpace | None = None


# ---------------------------------------------------------------------------
# M2 Evidence models
# ---------------------------------------------------------------------------

class Claim(BaseModel):
    text: str
    source_id: str
    confidence: float = Field(ge=0.0, le=1.0)


class Entity(BaseModel):
    name: str
    type: Literal["person", "location", "date", "operation"]
    source_ids: list[str]


class Relationship(BaseModel):
    source_a: str
    source_b: str
    type: str
    confidence: float = Field(ge=0.0, le=1.0)


class TemporalLink(BaseModel):
    source_a: str
    source_b: str
    gap_minutes: float


class Contradiction(BaseModel):
    claim_a: str
    claim_b: str
    source_a: str
    source_b: str
    conflict_type: ConflictType
    confidence: float = Field(ge=0.0, le=1.0)


# ---------------------------------------------------------------------------
# Evidence graph
# ---------------------------------------------------------------------------

class GraphNode(BaseModel):
    id: str
    label: str
    modality: Modality
    color: str
    confidence: float = Field(ge=0.0, le=1.0)


class GraphEdge(BaseModel):
    source: str
    target: str
    edge_type: EdgeType
    similarity: float
    temporal_gap: float | None = None


class EvidenceGraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class EvidenceResult(BaseModel):
    """
    Evidence output produced by M2 and consumed by M4.
    """

    claims: list[Claim]
    entities: list[Entity]
    relationships: list[Relationship]

    temporal_links: list[TemporalLink] = Field(default_factory=list)

    contradictions: list[Contradiction]
    graph: EvidenceGraph

    source_references: list[str]


# ---------------------------------------------------------------------------
# M4 → M3
# ---------------------------------------------------------------------------

class Citation(BaseModel):
    num: int
    source_id: str
    source_name: str
    modality: Modality

    page: int | None = None

    timestamp_start: float | None = None
    timestamp_end: float | None = None

    text: str


class SourceSummary(BaseModel):
    source_id: str
    file_name: str
    modality: Modality
    chunk_count: int
    status: Literal["indexed", "failed", "processing"]


class AQILAResponse(BaseModel):
    """
    Final response returned by M4 to M3.

    IMPORTANT:
    This model intentionally contains NO embedding fields.
    """

    query_id: str
    answer: str

    citations: list[Citation]

    contradiction_found: bool
    contradiction_detail: Contradiction | None = None

    evidence: EvidenceGraph
    sources: list[SourceSummary]

    response_time_ms: int


# ---------------------------------------------------------------------------
# Ingest API
# ---------------------------------------------------------------------------

class IngestUploadResponse(BaseModel):
    source_id: str
    status: Literal["processing", "indexed", "failed"]


class IngestStatusResponse(BaseModel):
    source_id: str
    status: Literal["processing", "indexed", "failed"]


# ---------------------------------------------------------------------------
# Query API
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str


# ---------------------------------------------------------------------------
# Generic health response
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str