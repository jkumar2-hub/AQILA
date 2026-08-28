# AQILA — Decisions Log
## Technical Decisions with Rationale + Date

**Owner:** All members. Any decision that affects another member must be logged here.  
**Rule:** Log BEFORE implementing cross-cutting changes. Never silently change something that another member depends on.

**Must include (per v4.1 §7, §18):**
- ChromaDB score conversion formula (confirmed value — M1 fills after Hours 2–5 testing)
- embedding_space values in use
- top-k strategy (P0 top-8, P1 candidate pool sizes)

---

## Log Format

```
### [DATE] — [AUTHOR / MEMBER] — [DECISION TITLE]
**Decision:** What was decided.
**Rationale:** Why this choice was made.
**Impact:** Which members / modules are affected.
**Action required:** What other members need to do (if anything).
```

---

## Standing Decisions (from v4.1)

These decisions are defined in the v4.1 implementation plan and are not subject to change without team agreement.

### 2026-08-28 — M4 (Repo Init) — Architecture: Modular Monolith
**Decision:** AQILA is a modular monolith. M1 (rag/) and M2 (evidence/) are Python modules inside the same FastAPI process. No microservices.  
**Rationale:** Reduces deployment complexity and inter-process latency for a 20-hour hackathon prototype.  
**Impact:** All members. No separate service ports for M1 or M2.  
**Action required:** None — established in v4.1.

### 2026-08-28 — M4 (Repo Init) — Embedding Space Strategy
**Decision:** Three ChromaDB collections with two embedding spaces: `"minilm"` (384-dim, documents_col + audio_col) and `"clip"` (512-dim, images_col, P1). Cross-space cosine comparison is prohibited.  
**Rationale:** MiniLM and CLIP produce incompatible vector spaces with different dimensions. Comparing them directly would produce meaningless or incorrect similarity scores.  
**Impact:** M1 (sets embedding_space on RetrievalResult), M2 (enforces same-space guard before cosine).  
**Action required:** M2 must check `embedding_space_i == embedding_space_j` before any pairwise cosine computation.

### 2026-08-28 — M4 (Repo Init) — Top-k Retrieval Strategy
**Decision:** P0 Golden Path: `documents_col → top-8 FINAL`. P1 Multimodal: `documents_col top-5 candidates + audio_col top-5 candidates + images_col top-3 candidates → score fusion → final top-8`.  
**Rationale:** Standardises the number of chunks passed to M2 and the LLM. Candidate pools allow per-modality diversity before fusion.  
**Impact:** M1 (retrieval implementation), M2 (receives exactly top-8 final), M4 (prompt construction).  
**Action required:** M1 enforces final top-8 for all paths. Never pass more than 8 chunks to M2 or the LLM.

### 2026-08-28 — M4 (Repo Init) — OLLAMA_BASE_URL Strategy
**Decision:** Never hardcode `localhost:11434` in application code. Always read `OLLAMA_BASE_URL` from environment. Dev = `http://localhost:11434`, Container = `http://ollama:11434` (Docker service name).  
**Rationale:** `localhost` inside a Docker container refers to that container only, not the host. Using the service name ensures container-to-container communication works correctly.  
**Impact:** M4 (backend configuration), M1 (generator.py Ollama calls).  
**Action required:** All Ollama HTTP calls must use the env var, not a hardcoded URL.

---

## Pending — REQUIRES VERIFICATION

### ⚠️ ChromaDB Score Conversion Formula — M1 MUST VERIFY IN HOURS 2–5

**Status:** REQUIRES VERIFICATION  
**Assigned to:** M1  
**Deadline:** Hour 7 (before first real integration)

**Context (per v4.1 §8):**  
ChromaDB raw distance → AQILA normalised score [0,1] conversion depends on:
- ChromaDB version installed
- `hnsw:space` setting for the collection
- Whether vectors are unit-normalised before storage

**Required action (M1):**
1. Create a test script with two known vectors of known cosine similarity
2. Insert into ChromaDB (documents_col configuration)
3. Query and record the raw distance returned
4. Compute the conversion formula that maps this raw distance to AQILA score ∈ [0,1]
5. Document the confirmed formula below and cross-reference in rag/retriever.py

**Application contract (unchanged):** `RetrievalResult.score ∈ [0.0, 1.0]` where 1.0 = most relevant.

**To fill in (M1, after Hours 2–5 testing):**
```
ChromaDB version: [TO BE FILLED BY M1]
hnsw:space setting: [TO BE FILLED BY M1]
Observed raw_distance range for known vectors: [TO BE FILLED BY M1]
Confirmed conversion formula: [TO BE FILLED BY M1]
  Example: score = 1 - raw_distance   (only if confirmed for this config)
  Example: score = 1 - (raw_distance / 2)   (if cosine space, range [0,2])
  Example: score = raw_distance   (if ChromaDB already returns similarity not distance)
Test vector pair used: [TO BE FILLED BY M1]
Expected cosine similarity: [TO BE FILLED BY M1]
Observed raw_distance: [TO BE FILLED BY M1]
Derived score (should be close to expected cosine): [TO BE FILLED BY M1]
```

---

## Future Decisions

_Log cross-cutting decisions here as they are made during the hackathon._

---

*AQILA SIH 2026 · Implementation Plan v4.1*
