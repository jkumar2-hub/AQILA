"""
AQILA — FastAPI Application Entry Point
Owner: M4 — Backend / Platform / Integration
"""



from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import init_db
from .api import ingest, query, sources, settings



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    # Initialize SQLite tables
    await init_db()

    print("AQILA backend started")
    print("SQLite database initialized")

    yield

    print("AQILA backend shutting down")


app = FastAPI(
    title="AQILA",
    description="Offline Multimodal RAG + Evidence Intelligence System",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# API Routers
# ---------------------------------------------------------

app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(sources.router)
app.include_router(settings.router)
# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "aqila-backend",
    }


@app.get("/api/health")
async def api_health_check():
    return {
        "status": "ok",
        "service": "aqila-backend",
    }