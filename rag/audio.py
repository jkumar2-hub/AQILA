import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel

from backend.app.db.chroma import audio_col
from .embedder import embed_text

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_whisper() -> WhisperModel:
    return WhisperModel(
        "base",
        device="cpu",
        compute_type="int8",
    )


def transcribe_audio(file_path: str | Path) -> list[dict[str, Any]]:
    """
    Transcribe audio with Faster-Whisper.

    Returns timestamped segments:
    {
        text,
        timestamp_start,
        timestamp_end
    }
    """
    file_path = str(file_path)

    segments, _ = _get_whisper().transcribe(
        file_path,
        beam_size=5,
    )

    results = []

    for segment in segments:
        text = segment.text.strip()

        if not text:
            continue

        results.append(
            {
                "text": text,
                "timestamp_start": float(segment.start),
                "timestamp_end": float(segment.end),
            }
        )

    return results


def index_audio(
    file_path: str | Path,
    source_id: str,
    file_name: str,
) -> int:
    """
    Transcribe and index audio segments into audio_col.
    """
    segments = transcribe_audio(file_path)

    if not segments:
        return 0

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for index, segment in enumerate(segments):
        text = segment["text"]

        ids.append(f"{source_id}:{index}")
        documents.append(text)

        embeddings.append(embed_text(text))

        metadatas.append(
            {
                "source_id": source_id,
                "file_name": file_name,
                "modality": "audio",
                "source_type": "audio",
                "chunk_index": index,
                "timestamp_start": segment["timestamp_start"],
                "timestamp_end": segment["timestamp_end"],
            }
        )

    audio_col.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(ids)
