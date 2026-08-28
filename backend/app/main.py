"""
backend/app/main.py
────────────────────────────────────────────────────────────────────────────
AQILA — FastAPI Application Entry Point
Owner: M4 — Backend / Platform / Integration

PLACEHOLDER — Implementation begins at Hour 0 of the hackathon.
Do not add application logic here during repository initialization.

Architecture: Modular Monolith.
M1 (rag/) and M2 (evidence/) run as Python modules inside this single
FastAPI process. No microservices, Kubernetes, or message brokers.

Responsibilities (per v4.1 §3 M4):
  - FastAPI app creation with CORS and lifespan events
  - DB init and model warmup on startup
  - API routing: ingest.py, query.py, sources.py, settings.py
  - M1 and M2 imported as Python modules (not services)
  - Strip embedding + embedding_space fields from RetrievalResult
    before assembling AQILAResponse for M3
  - LLM resource safety coordination (one heavyweight LLM at a time)
  - [P1] npm run build + FastAPI StaticFiles serving of frontend/dist/
  - [P1] Docker compose with correct Ollama service-name networking

Key env var: OLLAMA_BASE_URL
  - Dev:       http://localhost:11434
  - Container: http://ollama:11434  (Docker service name — NOT localhost)
  Never hardcode localhost in application code.

References:
  - docs/API_CONTRACTS.md  — frozen interface definitions
  - docs/ARCHITECTURE.md   — modular monolith design
  - backend/.env.example   — environment variable template
"""

# TODO (M4, Hour 0–2): Implement FastAPI app, CORS, lifespan, health check
