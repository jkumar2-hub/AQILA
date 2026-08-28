# AQILA — Data Schemas
## SQLite Tables · ChromaDB Collections · Pydantic Models

**Source:** AQILA Implementation Plan v4.1 §3, §8  
**Owner:** M4 (SQLite, ChromaDB setup); M1 (ChromaDB writes); M2 (ChromaDB reads via RetrievalResult)  
**Stage:** 🚧 Pre-Development — Schema defined, not yet implemented

---

## SQLite Tables (per v4.1 §3 M4)

### `sources` table (P0)

Tracks all ingested source files.

| Column | Type | Notes |
|---|---|---|
| `source_id` | TEXT PRIMARY KEY | UUID |
| `file_name` | TEXT NOT NULL | Original filename |
| `file_path` | TEXT | Path under `data/uploads/{source_id}/` |
| `source_type` | TEXT | `'pdf'` \| `'docx'` \| `'audio'` \| `'image'` |
| `modality` | TEXT | `'text'` \| `'audio'` \| `'image'` |
| `status` | TEXT | `'processing'` \| `'indexed'` \| `'failed'` |
| `chunk_count` | INTEGER | Number of indexed chunks |
| `file_created_at` | TEXT | ISO timestamp (for temporal edges, P1) |
| `created_at` | TEXT | Ingest timestamp |
| `error_message` | TEXT | Error detail if status = 'failed' |

### `queries` table (P0)

Tracks all user queries and their responses.

| Column | Type | Notes |
|---|---|---|
| `query_id` | TEXT PRIMARY KEY | UUID |
| `query_text` | TEXT NOT NULL | User's question |
| `answer` | TEXT | LLM-generated grounded answer |
| `response_time_ms` | INTEGER | End-to-end latency |
| `contradiction_found` | INTEGER | 0 or 1 (SQLite boolean) |
| `created_at` | TEXT | Query timestamp |

### `evidence_edges` table (P1)

Persisted graph edge records for past queries.

| Column | Type | Notes |
|---|---|---|
| `edge_id` | TEXT PRIMARY KEY | UUID |
| `query_id` | TEXT | FK → queries.query_id |
| `source_a` | TEXT | source_id of first node |
| `source_b` | TEXT | source_id of second node |
| `edge_type` | TEXT | `'semantic'` \| `'temporal'` \| `'both'` |
| `similarity` | REAL | Pairwise cosine similarity (same-space, M2-computed) |
| `temporal_gap` | REAL | Minutes (P1 only; NULL if not computed) |

---

## ChromaDB Collections (per v4.1 §8 + §3 M4)

### `documents_col`

Stores text chunk embeddings from PDF/DOCX files (and image captions, P1).

| Property | Value |
|---|---|
| Embedding model | all-MiniLM-L6-v2 |
| Dimensions | 384 |
| `embedding_space` metadata | `"minilm"` |
| Persistent path | `./data/chroma` |

**Required metadata per document:**

| Field | Type | Notes |
|---|---|---|
| `source_id` | str | UUID |
| `file_name` | str | Original filename |
| `source_type` | str | `'pdf'` \| `'docx'` \| `'image'` (caption) |
| `modality` | str | `'text'` |
| `page_number` | int \| None | |
| `chunk_index` | int | |
| `file_created_at` | str \| None | ISO timestamp |
| `embedding_space` | str | `"minilm"` (always) |

### `audio_col` (P1)

Stores audio transcript segment embeddings from faster-whisper.

| Property | Value |
|---|---|
| Embedding model | all-MiniLM-L6-v2 |
| Dimensions | 384 |
| `embedding_space` metadata | `"minilm"` |

**Additional metadata:**

| Field | Type | Notes |
|---|---|---|
| `timestamp_start` | float | Segment start (seconds) |
| `timestamp_end` | float | Segment end (seconds) |
| `segment_index` | int | |

### `images_col` (P1)

Stores CLIP image embeddings. Different vector space from `documents_col` / `audio_col`.

| Property | Value |
|---|---|
| Embedding model | OpenCLIP ViT-B-32 |
| Dimensions | **512** (incompatible with MiniLM 384-dim) |
| `embedding_space` metadata | `"clip"` |

> ⚠️ **Critical:** Never mix `images_col` embeddings with `documents_col` / `audio_col` embeddings in any cosine computation. They are different dimensional spaces.

---

## Pydantic Models

Implemented by M4 in `backend/app/schemas/`. All shapes must match `docs/API_CONTRACTS.md`.

**Key models:**
- `RetrievalResult` — includes `embedding` and `embedding_space` (stripped before AQILAResponse)
- `EvidenceResult` — from M2
- `AQILAResponse` — sent to M3 (no embedding, no embedding_space)
- `Citation`, `Contradiction`, `EvidenceGraph`, `GraphNode`, `GraphEdge`
- `IngestUploadResponse`, `IngestStatusResponse`
- `SourceSummary`, `SettingsStatusResponse`

See `docs/API_CONTRACTS.md` for field-level definitions.

---

## ChromaDB Score Conversion Note (per v4.1 §8)

> **⚠️ REQUIRES VERIFICATION (M1, Hours 2–5)**  
> ChromaDB raw distance must be converted to AQILA normalised score ∈ [0,1].  
> Do NOT assume `raw_distance ∈ [0,1]`. The actual range depends on ChromaDB version,  
> `hnsw:space` setting, and whether vectors are unit-normalised.  
> M1 tests with known vectors and documents the confirmed formula in `docs/DECISIONS_LOG.md`.  
> M4 and M2 trust `RetrievalResult.score` and do not re-interpret it.

---

*AQILA SIH 2026 · Implementation Plan v4.1*
