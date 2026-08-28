# AQILA — API Contracts
## Interface Definitions · Frozen at Hour 2 of the Hackathon

**Source of truth:** AQILA Implementation Plan v4.1 §5  
**Status:** READ-ONLY after Hour 2. Breaking changes require team notification before implementation.  
**Owner:** All members (M4 coordinates)

> ⚠️ **CONTRACT FREEZE RULE**  
> After Hour 2, no member may change these contracts without communicating to the entire team first.  
> Coding AIs must read this file for interface definitions and implement to these contracts exactly.

---

## RetrievalResult (M1 → M2, M4)

```python
query: str
source_id: str               # UUID
source_type: str             # 'pdf' | 'docx' | 'audio' | 'image'
chunk_id: str                # UUID
text: str                    # chunk text or image caption
score: float                 # 0.0–1.0 AQILA normalised relevance score
                             # (see DECISIONS_LOG.md for confirmed conversion formula)
modality: str                # 'text' | 'audio' | 'image'
page_number: int | None      # text modality
timestamp_start: float | None  # audio (seconds)
timestamp_end: float | None
file_name: str
file_created_at: str | None  # ISO timestamp (for temporal edges, P1)
metadata: dict               # extra per-modality fields

embedding: list[float] | None
# OPTIONAL. M1 populates from ChromaDB retrieval (include=['embeddings']).
# No re-computation. M2 uses this for pairwise cosine similarity (graph edges).
# M4 strips this field before forwarding AQILAResponse to M3.
# M2 must NOT import rag/embedder.py directly.

embedding_space: str | None
# REQUIRED when embedding is not None.
# Values: "minilm" (384-dim, MiniLM text embeddings)
#         "clip"   (512-dim, CLIP image embeddings, P1 only)
# M2 must ONLY compute pairwise cosine between results
# that share the same embedding_space.
# MiniLM ↔ MiniLM: valid.
# CLIP ↔ CLIP: valid.
# MiniLM ↔ CLIP: PROHIBITED — different vector spaces, incompatible dimensions.
# M4 strips this field before forwarding AQILAResponse to M3.
```

> **`score` vs `embedding`:**  
> `score` = AQILA normalised relevance score for this chunk against the query (query→chunk).  
> `embedding` = the chunk's own vector representation.  
> These are different quantities. M2 uses `embedding` for pairwise chunk-to-chunk similarity (graph edges). M2 does NOT use `score` for graph construction.

> **`embedding_space` rule:**  
> Two embeddings may only be compared if they have the same `embedding_space` value.  
> P0 graph uses only `"minilm"` embeddings. CLIP embeddings (`"clip"`) appear only in P1 multimodal results and must never be compared with MiniLM embeddings.

---

## EvidenceResult (M2 → M4)

```python
claims: list[Claim]
    Claim.text: str
    Claim.source_id: str
    Claim.confidence: float        # 0.0–1.0

entities: list[Entity]
    Entity.name: str
    Entity.type: str               # 'person' | 'location' | 'date' | 'operation'
    Entity.source_ids: list[str]

relationships: list[Relationship]
    Relationship.source_a: str     # source_id
    Relationship.source_b: str     # source_id
    Relationship.type: str
    Relationship.confidence: float

temporal_links: list[TemporalLink]  # P1 — empty list if not yet implemented
    TemporalLink.source_a: str
    TemporalLink.source_b: str
    TemporalLink.gap_minutes: float

contradictions: list[Contradiction]
graph: EvidenceGraph
source_references: list[str]       # source_ids used
```

---

## AQILAResponse (M4 → M3)

```python
query_id: str
answer: str                        # LLM output with [N] markers
citations: list[Citation]
contradiction_found: bool
contradiction_detail: Contradiction | None
evidence: EvidenceGraph
sources: list[SourceSummary]
response_time_ms: int
# NOTE: No embedding or embedding_space fields.
# M4 strips them before this response is built.
```

---

## Citation

```python
num: int            # matches [N] in answer
source_id: str
source_name: str    # file_name
modality: str       # 'text' | 'audio' | 'image'
page: int | None
timestamp_start: float | None
timestamp_end: float | None
text: str           # 200-char snippet
```

---

## Contradiction

```python
claim_a: str
claim_b: str
source_a: str       # source_id
source_b: str       # source_id
conflict_type: str  # 'date' | 'name' | 'location' | 'fact'
confidence: float   # 0.0–1.0
```

---

## EvidenceGraph (nodes + edges)

```python
nodes: list[GraphNode]
    GraphNode.id: str           # source_id
    GraphNode.label: str        # file_name
    GraphNode.modality: str     # 'text' | 'audio' | 'image'
    GraphNode.color: str        # hex: teal=#1D9E75, amber=#EF9F27, purple=#534AB7
    GraphNode.confidence: float

edges: list[GraphEdge]
    GraphEdge.source: str       # node id
    GraphEdge.target: str       # node id
    GraphEdge.edge_type: str    # 'semantic' | 'temporal' | 'both'
    GraphEdge.similarity: float
    # Pairwise cosine similarity between chunk embeddings (M2-computed from RetrievalResult.embedding).
    # ONLY computed between chunks sharing the same embedding_space.
    # NOT the query→chunk retrieval score.
    GraphEdge.temporal_gap: float | None   # minutes (P1 only; None if not computed)
```

---

## SourceSummary (in AQILAResponse)

```python
source_id: str
file_name: str
modality: str       # 'text' | 'audio' | 'image'
chunk_count: int
status: str         # 'indexed' | 'failed' | 'processing'
```

---

## API Endpoints

### P0 — Required by Hour 10

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/ingest/upload` | Upload file → triggers background ingest → returns `{source_id, status}` |
| `GET` | `/api/ingest/status/{source_id}` | Returns current ingest status lifecycle |
| `POST` | `/api/query` | Full RAG + evidence pipeline → returns `AQILAResponse` |
| `GET` | `/api/query/{query_id}/evidence` | Returns `EvidenceGraph` JSON for a past query |

### P1 — Target Hours 10–15

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/sources` | List all ingested sources |
| `DELETE` | `/api/sources/{source_id}` | Delete source + its ChromaDB chunks |
| `GET` | `/api/settings/status` | Ollama health, model status |

---

## Embedding Space Reference

| Collection | Model | Dimensions | embedding_space | Notes |
|---|---|---|---|---|
| `documents_col`, `audio_col` | all-MiniLM-L6-v2 | 384-dim | `"minilm"` | Both text-based, compatible space |
| `images_col` | OpenCLIP ViT-B-32 | 512-dim | `"clip"` | Separate collection; P1 only |

**Cross-space comparison rule:**
- `"minilm"` ↔ `"minilm"`: ✅ valid — M2 may compute pairwise cosine
- `"clip"` ↔ `"clip"`: ✅ valid — M2 may compute pairwise cosine (P1)
- `"minilm"` ↔ `"clip"`: ❌ PROHIBITED — incompatible dimensions

---

## Retrieval Strategy

| Path | Strategy |
|---|---|
| **P0 Golden Path** | `documents_col` → **top-8 FINAL** results |
| **P1 Multimodal** | `documents_col` → top-5 candidates, `audio_col` → top-5 candidates, `images_col` → top-3 candidates → score fusion → final top-8 |

> "top-5" always refers to P1 per-modality intermediate candidates only. Final list is always top-8.

---

## Node Colour Reference

| Modality | Colour | Hex |
|---|---|---|
| Document (PDF/DOCX) | Teal | `#1D9E75` |
| Audio | Amber | `#EF9F27` |
| Image | Purple | `#534AB7` |

---

*Frozen after Hour 2 · AQILA SIH 2026 · Implementation Plan v4.1*
