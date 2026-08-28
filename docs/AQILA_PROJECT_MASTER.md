# AQILA — Project Master
## Overview · Vision · Team Map · Demo Goal

**Project:** AQILA — Find the connection, not just the document.  
**Competition:** Smart India Hackathon 2026 · Problem Statement 25231  
**Subtitle:** Offline Multimodal Evidence Intelligence  
**Stage:** 🚧 Repository Initialization / Pre-Development

---

## What is AQILA?

AQILA is an **offline-first, multimodal intelligence tool** that ingests documents (PDF, DOCX), audio recordings, and images; indexes them in a local vector store; and answers natural-language questions with **grounded, citation-backed responses** supported by an **Evidence Chain Graph**.

Every answer is traceable to an exact source, page, or audio timestamp. AQILA can detect **contradictions** across sources and visualise the **semantic and temporal relationships** between them — all without an internet connection.

---

## Core Demonstration Goal (per v4.1 §1)

1. Launch AQILA fully offline
2. Load / upload controlled demo dataset
3. Ingest PDF (and optionally audio / image)
4. Ask a natural-language question
5. Receive a grounded answer with [N] citation markers
6. Click a citation → see exact source / page / timestamp
7. View Evidence Chain Graph (nodes = sources, edges = relationships)
8. See contradiction banner when two sources conflict
9. Confirm zero internet required for any of the above

---

## Preserved AQILA Features (per v4.1 §2)

| Feature | Description |
|---|---|
| **Fully Offline Operation** | Zero network calls at runtime. WiFi disconnected = identical operation. |
| **Multimodal RAG** | Unified retrieval across PDF/DOCX text, audio transcripts, and image captions. |
| **PDF / DOCX Ingestion** | Docling (layout-aware, primary) + PyMuPDF fallback. Chunk size 400 tokens, 50-token overlap. |
| **Audio Transcription** | faster-whisper (base model, CPU int8). Word-level timestamps. ~200-word segments. (P1) |
| **Image Understanding** | Vision LLM generates caption. Extended capability; must gracefully degrade on constrained hardware. (P1) |
| **Grounded LLM Answers** | llama3.2:3b via Ollama. Context is ONLY retrieved chunks. Temperature 0.1. |
| **Exact Citations** | Every [N] maps to source file, page number or audio timestamp, and chunk snippet. |
| **Evidence Chain Graph** | NetworkX. Nodes = source files. Edges = semantic (pairwise cosine > 0.6, same embedding space) or temporal (±10 min, P1). |
| **Contradiction Detection** | Two-stage: deterministic claim check → LLM verification on candidates only. P0 = text-only. |
| **Source Traceability** | Every chunk tagged: source_id, file_name, modality, page/timestamp, chunk_index. |
| **Offline-First Deployment** | All models pre-pulled. Ethernet unplugged = identical operation. |

---

## Team Ownership Structure (per v4.1 §3)

| Member | Role | Owns |
|---|---|---|
| **M1** | AI / ML + RAG Core | `rag/` |
| **M2** | Evidence Intelligence | `evidence/` |
| **M3** | Frontend / UX | `frontend/` |
| **M4** | Backend / Platform / Integration | `backend/` + integration |

**Architecture:** Modular Monolith. M1 (`rag/`) and M2 (`evidence/`) are Python modules running inside the single FastAPI process managed by M4. Not microservices.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.11) |
| Database | SQLite + SQLAlchemy (async, aiosqlite) |
| Vector Store | ChromaDB (local persistent) |
| LLM | Ollama · llama3.2:3b (P0) · llama3.2-vision:11b (P1) |
| Text Embeddings | sentence-transformers all-MiniLM-L6-v2 (384-dim) |
| Image Embeddings | OpenCLIP ViT-B-32 (512-dim) (P1) |
| Audio | faster-whisper base model (P1) |
| Graph | NetworkX |
| Frontend | React 18 + Vite 5 + TailwindCSS + shadcn/ui + TanStack Query v5 |
| Visualization | react-force-graph-2d |

---

## Branch Strategy (per v4.1 §6)

| Branch | Purpose |
|---|---|
| `main` | Demo-verified code only. M4 merges here after integration tests pass. |
| `develop` | Integration branch. Feature branches merge here. M4 coordinates conflicts. |
| `feature/m1-rag` | M1 branch. Self-tested before merge. |
| `feature/m2-evidence` | M2 branch. Self-tested before merge. |
| `feature/m3-frontend` | M3 branch. Self-tested before merge. |
| `feature/m4-backend` | M4 branch. Integration, orchestration, end-to-end testing. |

---

## Status

> This document will be updated by M4 at each integration milestone.  
> See `docs/INTEGRATION_STATUS.md` for the live integration state.

*AQILA SIH 2026 · Implementation Plan v4.1 · Pre-Development Stage*
