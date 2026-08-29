"""
AQILA — Settings API Router

Owner: M4 — Backend / Platform / Integration

P1 endpoint:
    GET /api/settings/status
"""

import os

import httpx
from fastapi import APIRouter


router = APIRouter(
    prefix="/api/settings",
    tags=["settings"],
)


@router.get("/status")
async def settings_status():
    """
    Return Ollama health and configured model status.
    """

    ollama_base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434",
    )

    ollama_model = os.getenv(
        "OLLAMA_MODEL",
        "llama3.2:3b",
    )

    ollama_status = "offline"

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(
                f"{ollama_base_url}/api/tags"
            )

            if response.status_code == 200:
                ollama_status = "online"

    except Exception:
        ollama_status = "offline"

    return {
        "ollama": {
            "status": ollama_status,
            "base_url": ollama_base_url,
            "model": ollama_model,
        },
    }