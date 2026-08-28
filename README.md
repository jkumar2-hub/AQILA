# AQILA
## Find the connection, not just the document.

**Smart India Hackathon 2026 · Problem Statement 25231**  
**Offline Multimodal Evidence Intelligence**

> 🚧 **Repository Status: Initialization / Pre-Development**  
> The repository structure has been initialized per Implementation Plan v4.1.  
> No application code has been implemented yet.  
> Development begins at Hour 0 of the hackathon.

---

## What is AQILA?

AQILA is an **offline-first, multimodal intelligence tool** that:

- Ingests **PDF, DOCX, audio, and image** files into a local vector store
- Answers natural-language questions with **grounded, citation-backed responses**
- Detects **contradictions** across sources automatically
- Visualises **semantic and temporal relationships** between sources as an Evidence Chain Graph
- Operates with **zero internet connection** — all models run locally

---

## Team

| Member | Role | Module Ownership |
|---|---|---|
| M1 | AI / ML + RAG Core | `rag/` |
| M2 | Evidence Intelligence | `evidence/` |
| M3 | Frontend / UX | `frontend/` |
| M4 | Backend / Platform / Integration | `backend/` + integration |

**Architecture:** Modular Monolith — all modules run in one FastAPI process.

---

## Repository Structure

```
AQILA/
├── backend/                   # M4 — FastAPI app, SQLite, ChromaDB client
│   └── app/
│       ├── api/               # ingest.py, query.py, sources.py, settings.py
│       ├── db/                # models.py, database.py, chroma.py
│       └── schemas/           # Pydantic request/response models
├── rag/                       # M1 — Parsing, embedding, retrieval, generation
│   └── tests/
│       └── mock_retrieval.py  # Mock RetrievalResult (with embedding + embedding_space)
├── evidence/                  # M2 — Claim extraction, graph, contradiction
│   └── tests/
│       └── mock_evidence.py   # Mock EvidenceResult
├── frontend/                  # M3 — React 18 + Vite 5 + TailwindCSS
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       ├── mocks/
│       │   └── mock_response.json   # Mock AQILAResponse (no embeddings)
│       └── lib/
├── docs/                      # Shared documentation
│   ├── AQILA_PROJECT_MASTER.md
│   ├── ARCHITECTURE.md
│   ├── API_CONTRACTS.md       # Frozen at Hour 2
│   ├── DATA_SCHEMAS.md
│   ├── INTEGRATION_STATUS.md  # Updated by each member at milestones
│   └── DECISIONS_LOG.md       # Cross-cutting technical decisions
├── demo_data/                 # Controlled demo dataset (committed)
├── data/                      # Runtime data — GITIGNORED
├── models/                    # Model weights — GITIGNORED
└── scripts/                   # Setup and verification scripts
```

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Demo-verified code only. M4 merges here after integration tests pass. |
| `develop` | Integration branch. Feature branches merge here. |
| `feature/m1-rag` | M1 — AI/ML + RAG Core |
| `feature/m2-evidence` | M2 — Evidence Intelligence |
| `feature/m3-frontend` | M3 — Frontend / UX |
| `feature/m4-backend` | M4 — Backend / Platform / Integration |

**Rules:** Never push directly to `main`. Self-test before merging to `develop`. Breaking contract changes require team notification.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.11) · SQLite + SQLAlchemy · aiosqlite |
| Vector Store | ChromaDB (local persistent) |
| LLM | Ollama · llama3.2:3b (P0) · llama3.2-vision:11b (P1, optional) |
| Text Embeddings | sentence-transformers all-MiniLM-L6-v2 (384-dim) |
| Image Embeddings | OpenCLIP ViT-B-32 (512-dim) (P1) |
| Audio | faster-whisper base model, CPU int8 (P1) |
| Graph | NetworkX |
| Frontend | React 18 · Vite 5 · TailwindCSS · shadcn/ui · TanStack Query v5 |
| Graph Viz | react-force-graph-2d |

---

## Pre-Hackathon Setup (Required Before Hour 0)

> ⚠️ **OFFLINE REQUIREMENT**: All models and dependencies must be downloaded and verified **before** the hackathon. There must be zero runtime model downloads, no pip downloads, no npm downloads, and no internet dependencies during the hackathon or demo.

### 1. Clone and branch

```bash
git clone https://github.com/jkumar2-hub/AQILA.git
cd AQILA
git checkout develop
git checkout -b feature/m<N>-<role>   # your feature branch
```

### 2. Python dependencies (P0 — required before hackathon)

```bash
# The .venv is already configured. Activate it:
# Windows:
.venv\Scripts\activate
# Then install:
pip install -r backend/requirements.txt
```

### 3. Ollama setup (P0 — required before hackathon)

```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2:3b           # 2.2 GB — REQUIRED
ollama serve                       # verify at http://localhost:11434
```

### 4. Pre-cache MiniLM model (P0 — required before hackathon)

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### 5. Frontend (P0 — required before hackathon)

```bash
cd frontend
npm install   # complete before hackathon
```

### 6. Environment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env if needed (OLLAMA_BASE_URL, etc.)
```

### 7. P1 models (optional — if hardware allows)

```bash
ollama pull llama3.2-vision:11b   # 7.5 GB — P1 optional
pip install faster-whisper open-clip-torch python-docx
```

---

## Development (Hour 0 Onwards)

```bash
# Terminal 1 — Ollama
ollama serve

# Terminal 2 — Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 3 — Frontend (dev mode)
cd frontend
npm run dev   # Vite dev server at :5173, proxies /api/* to :8000
```

Open: `http://localhost:5173`

---

## Documentation

| Document | Purpose |
|---|---|
| [`docs/AQILA_PROJECT_MASTER.md`](docs/AQILA_PROJECT_MASTER.md) | Project overview, team map, demo goal |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System diagram, data flow, modular monolith |
| [`docs/API_CONTRACTS.md`](docs/API_CONTRACTS.md) | Frozen interface definitions (read-only after Hour 2) |
| [`docs/DATA_SCHEMAS.md`](docs/DATA_SCHEMAS.md) | SQLite tables, ChromaDB collections, Pydantic models |
| [`docs/INTEGRATION_STATUS.md`](docs/INTEGRATION_STATUS.md) | Live integration state — updated by each member |
| [`docs/DECISIONS_LOG.md`](docs/DECISIONS_LOG.md) | Technical decisions with rationale |

---

## P0 / P1 / P2 Priority

- **P0 — Core Demo (by Hour 10):** PDF ingestion → MiniLM embeddings → ChromaDB → text retrieval top-8 → llama3.2:3b grounded answer → citations → contradiction detection → evidence graph → React UI
- **P1 — Extended (Hours 10–15):** DOCX · Audio (Whisper) · Image (CLIP + vision) · multimodal score fusion · temporal edges · Sources/Settings pages · Docker
- **P2 — Optional:** Voice query · folder watcher · federated query · advanced reranking

---

*AQILA SIH 2026 · Implementation Plan v4.1 · 4 Members · 20 Hours · Modular Monolith · Offline Multimodal Evidence Intelligence*
