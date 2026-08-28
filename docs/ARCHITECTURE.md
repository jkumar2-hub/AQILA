# AQILA — System Architecture
## System Diagram · Data Flow · Modular Monolith Model

**Source:** AQILA Implementation Plan v4.1 §4, §8  
**Stage:** 🚧 Pre-Development — Architecture defined, not yet implemented

---

## Architecture Model: Modular Monolith

AQILA is a **modular monolith**. M1 (`rag/`) and M2 (`evidence/`) are Python modules that run inside the **same FastAPI process** managed by M4. They are NOT microservices, NOT separate containers, NOT REST-connected services.

```
FastAPI (single process — M4 owns)
├── /api/ingest.py    ← imports rag.parsers, rag.embedder, rag.retriever
├── /api/query.py     ← imports rag.retriever, evidence.engine, rag.generator
├── /api/sources.py   ← imports storage layer
└── /api/settings.py  ← system health
```

**Do NOT introduce:** Kubernetes, service mesh, message brokers, REST microservices between M1 and M2, distributed infrastructure.

---

## Runtime Data Flow

```
[M1 AI/RAG]
  --RetrievalResult(+embedding, +embedding_space)-->
[M2 Evidence]
  --EvidenceResult-->
[M4 Backend]
  --AQILAResponse(embedding stripped, embedding_space stripped)-->
[M3 Frontend]
```

### Detailed P0 Golden Path Flow

```
Offline startup
  ↓
PDF ingestion (M1)
  ↓
Docling/PyMuPDF parse → chunks
  ↓
MiniLM embedding (384-dim, embedding_space="minilm")
  ↓
ChromaDB documents_col store (with embeddings)
  ↓
[M4] POST /api/ingest/upload → BackgroundTask → status polling
  ↓
[M3] Upload page → progress bar → "indexed" confirmation
  ↓
[M3] User types question → POST /api/query
  ↓
[M1] MiniLM embed query → documents_col → top-8 FINAL retrieval
     → RetrievalResult list WITH embedding (384-dim) AND embedding_space="minilm"
     → confirmed score conversion → RetrievalResult.score ∈ [0,1]
  ↓
[M2] Pairwise cosine (same-space: all "minilm") → semantic graph edges
     Claim extraction → text-based contradiction detection
     EvidenceGraph JSON
  ↓
[M1] Build prompt (text content only, no embeddings in prompt)
     → Ollama llama3.2:3b → grounded answer with [N] → Citations
  ↓
[M4] Assemble AQILAResponse (strip embedding + embedding_space) → return to M3
  ↓
[M3] Render answer → citation pills → contradiction banner → "View Evidence"
  ↓
[M3] Evidence page → react-force-graph-2d renders nodes + semantic edges
```

---

## Embedding Strategy

Three ChromaDB collections use **different embedding spaces**. They are NOT unified. Embeddings from different spaces must never be compared.

| Collection | Model | Dimensions | embedding_space | Notes |
|---|---|---|---|---|
| `documents_col`, `audio_col` | all-MiniLM-L6-v2 | 384-dim | `"minilm"` | Both text-based, compatible |
| `images_col` | OpenCLIP ViT-B-32 | 512-dim | `"clip"` | Separate collection (P1) |

**Cross-space comparison rule:**
- `"minilm"` ↔ `"minilm"`: ✅ valid
- `"clip"` ↔ `"clip"`: ✅ valid (P1)
- `"minilm"` ↔ `"clip"`: ❌ PROHIBITED

---

## Development Mode Networking

```
Browser → Vite :5173 → (/api/* proxied) → FastAPI :8000 → Ollama :11434
```

All three are local processes. `localhost` works during development.

## Container / Demo Mode Networking (P1)

```yaml
# docker-compose.yml — critical networking rule
services:
  ollama:
    image: ollama/ollama
    ports: ["11434:11434"]
  backend:
    build: ./backend
    environment:
      OLLAMA_BASE_URL: http://ollama:11434   # Docker service name — NOT localhost
```

> ⚠️ `localhost` inside a Docker container refers to THAT CONTAINER only. Use Docker service names for inter-container communication.

---

## LLM Resource Safety (per v4.1 §8)

On ~16 GB RAM / CPU-first hardware, only ONE heavyweight LLM (>1 GB) should be active at a time during the demo, unless hardware testing proves otherwise.

- Load `llama3.2:3b` first; keep resident for all generation + contradiction LLM calls.
- Load `llama3.2-vision:11b` only for image captioning (P1). Avoid simultaneous loading without testing.
- Set `OLLAMA_MAX_LOADED_MODELS=1` if memory pressure occurs.
- M4 coordinates model startup order. No job queue or distributed system required.

---

## Performance Targets (per v4.1 §8)

| Metric | Target |
|---|---|
| Hardware | 16 GB RAM, no GPU, CPU-only inference, SSD |
| PDF ingest | < 15s for 2-page doc |
| Query end-to-end | < 30s (retrieve + LLM + evidence) |
| Full demo path | < 35s |
| Acceptable max | ≤ 45s (if contradiction LLM call adds time) |
| Fallback | Switch to llama3.2:1b if > 35s |

---

*AQILA SIH 2026 · Implementation Plan v4.1 · Architecture unchanged from v4*
