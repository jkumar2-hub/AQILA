# AQILA — Integration Status
## Live Integration State per Member

**Owner:** All members update this file at milestones. M4 coordinates via this.  
**Format:** Update your section when you reach a milestone. Do not silently ignore bugs.

---

## Current Status

> **Stage:** 🚧 Repository Initialization — No implementation has started.
> 
> All members: update your section as you reach milestones during the hackathon.

---

## M1 — AI / ML + RAG Core (`rag/`)

| Milestone | Target Hour | Status | Notes |
|---|---|---|---|
| MiniLM singleton + ChromaDB write test | H0–2 | ⬜ Not started | |
| `mock_retrieval.py` with embedding + embedding_space | H0–2 | ⬜ Not started | |
| PDF parsing (Docling + PyMuPDF fallback) | H2–5 | ⬜ Not started | |
| Score conversion tested with known vectors | H2–5 | ⬜ Not started | **Document result in DECISIONS_LOG.md** |
| Text retrieval top-8 returning RetrievalResult | H5–7 | ⬜ Not started | |
| Ollama LLM generation + citation extraction | H7–10 | ⬜ Not started | |
| P0 Golden Path complete | H10 | ⬜ Not started | |
| DOCX + Audio + Image (P1) | H10–15 | ⬜ Not started | |

**Known issues:** _None yet_

---

## M2 — Evidence Intelligence (`evidence/`)

| Milestone | Target Hour | Status | Notes |
|---|---|---|---|
| Evidence data structures defined | H0–2 | ⬜ Not started | |
| `mock_evidence.py` with EvidenceResult shape | H0–2 | ⬜ Not started | |
| Pairwise cosine skeleton + same-space guard | H0–2 | ⬜ Not started | |
| Claim extractor (LLM) working | H2–5 | ⬜ Not started | |
| Graph builder (NetworkX, semantic edges) | H2–5 | ⬜ Not started | |
| Contradiction detector (text-based) | H5–7 | ⬜ Not started | |
| March 15 vs March 25 contradiction fires | H5–7 | ⬜ Not started | |
| EvidenceGraph JSON exported | H7–10 | ⬜ Not started | |
| Temporal edges (P1) | H10–15 | ⬜ Not started | |

**Known issues:** _None yet_

---

## M3 — Frontend / UX (`frontend/`)

| Milestone | Target Hour | Status | Notes |
|---|---|---|---|
| Vite + React + Tailwind scaffold | H0–2 | ⬜ Not started | |
| Sidebar + routing | H0–2 | ⬜ Not started | |
| Upload page (mock data) | H0–2 | ⬜ Not started | |
| Query page (mock_response.json) | H0–2 | ⬜ Not started | |
| Real API integration (TanStack Query) | H5–7 | ⬜ Not started | |
| Citation drawer working | H5–7 | ⬜ Not started | |
| Contradiction banner working | H5–7 | ⬜ Not started | |
| Evidence page (react-force-graph-2d) | H7–10 | ⬜ Not started | |
| P0 empty/loading/error states (Upload, Query, Evidence) | H7–10 | ⬜ Not started | |
| Sources + Settings pages (P1) | H10–15 | ⬜ Not started | |

**Known issues:** _None yet_

---

## M4 — Backend / Platform (`backend/`)

| Milestone | Target Hour | Status | Notes |
|---|---|---|---|
| FastAPI app + health check | H0–2 | ⬜ Not started | |
| SQLite init + ChromaDB collections | H0–2 | ⬜ Not started | |
| All API routes return 200 (skeleton) | H0–2 | ⬜ Not started | |
| POST /ingest/upload + BackgroundTask | H2–5 | ⬜ Not started | |
| POST /query wired to M1 (mock stub) | H2–5 | ⬜ Not started | |
| M2 integration + embedding strip confirmed | H5–7 | ⬜ Not started | |
| End-to-end curl test passes | H5–7 | ⬜ Not started | |
| End-to-end timing < 35s | H7–10 | ⬜ Not started | |
| Offline verification (ethernet disconnected) | H17–19 | ⬜ Not started | |
| Git tag v1.0-demo | H19 | ⬜ Not started | |

**Known issues:** _None yet_

---

## Integration Checkpoints (per v4.1 §12)

| Checkpoint | Target | Status |
|---|---|---|
| Hour 2 — Contract Freeze | API_CONTRACTS.md committed | ⬜ |
| Hour 5–7 — First Real Integration | Real PDF → ChromaDB; M2 receives real embeddings | ⬜ |
| Hour 10 — Golden Path Complete | End-to-end < 35s, offline, contradiction fires | ⬜ |
| Hour 15–17 — Full Integration | All P1 components working | ⬜ |
| Hour 19 — Architecture Freeze | Bug fixes only; tag v1.0-demo | ⬜ |

---

## Legend

| Symbol | Meaning |
|---|---|
| ⬜ Not started | Not yet begun |
| 🔄 In progress | Currently being worked on |
| ✅ Done | Self-tested and working |
| ❌ Blocked | Blocked — see known issues |
| ⚠️ Degraded | Working with known limitations |

---

*AQILA SIH 2026 · Updated at each milestone by each member*
