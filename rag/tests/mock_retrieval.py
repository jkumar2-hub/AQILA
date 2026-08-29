"""
AQILA — Mock RetrievalResult Fixture

Used by M1/M2 during independent development.

Contains realistic text-only RetrievalResult dictionaries
with 384-dimensional MiniLM embeddings.
"""

import math
import random
from uuid import uuid4


def _random_unit_vector(dim: int = 384) -> list[float]:
    """Generate a random unit vector."""
    vec = [random.gauss(0, 1) for _ in range(dim)]

    magnitude = math.sqrt(sum(x * x for x in vec))

    return [x / magnitude for x in vec]


SOURCE_A = str(uuid4())
SOURCE_B = str(uuid4())

CHUNK_A1 = str(uuid4())
CHUNK_A2 = str(uuid4())
CHUNK_B1 = str(uuid4())
CHUNK_B2 = str(uuid4())


MOCK_RETRIEVAL_RESULTS = [
    {
        "query": "What was the operation date?",
        "source_id": SOURCE_A,
        "source_type": "pdf",
        "chunk_id": CHUNK_A1,
        "text": (
            "The operation was conducted in Sector 7 on "
            "March 15, 2026. Agent Mehra confirmed presence "
            "at the location."
        ),
        "score": 0.95,
        "modality": "text",
        "page_number": 1,
        "timestamp_start": None,
        "timestamp_end": None,
        "file_name": "field_report.pdf",
        "file_created_at": "2026-03-15T03:00:00Z",
        "metadata": {},
        "embedding": _random_unit_vector(384),
        "embedding_space": "minilm",
    },
    {
        "query": "What was the operation date?",
        "source_id": SOURCE_A,
        "source_type": "pdf",
        "chunk_id": CHUNK_A2,
        "text": (
            "The field team reported that Agent Mehra "
            "arrived at Sector 7 before the operation began."
        ),
        "score": 0.88,
        "modality": "text",
        "page_number": 2,
        "timestamp_start": None,
        "timestamp_end": None,
        "file_name": "field_report.pdf",
        "file_created_at": "2026-03-15T03:00:00Z",
        "metadata": {},
        "embedding": _random_unit_vector(384),
        "embedding_space": "minilm",
    },
    {
        "query": "What was the operation date?",
        "source_id": SOURCE_B,
        "source_type": "pdf",
        "chunk_id": CHUNK_B1,
        "text": (
            "The operation was conducted in Sector 7 on "
            "March 25, 2026. Agent Mehra was listed as "
            "present at the location."
        ),
        "score": 0.91,
        "modality": "text",
        "page_number": 1,
        "timestamp_start": None,
        "timestamp_end": None,
        "file_name": "field_report_b.pdf",
        "file_created_at": "2026-03-25T03:00:00Z",
        "metadata": {},
        "embedding": _random_unit_vector(384),
        "embedding_space": "minilm",
    },
    {
        "query": "What was the operation date?",
        "source_id": SOURCE_B,
        "source_type": "pdf",
        "chunk_id": CHUNK_B2,
        "text": (
            "The report states that the field team "
            "completed the Sector 7 operation successfully."
        ),
        "score": 0.84,
        "modality": "text",
        "page_number": 2,
        "timestamp_start": None,
        "timestamp_end": None,
        "file_name": "field_report_b.pdf",
        "file_created_at": "2026-03-25T03:00:00Z",
        "metadata": {},
        "embedding": _random_unit_vector(384),
        "embedding_space": "minilm",
    },
]