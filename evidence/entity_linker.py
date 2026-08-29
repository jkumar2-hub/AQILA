"""
AQILA — Entity Linking Module

Owner: M2 — Evidence Intelligence

Extracts deterministic entities from retrieved evidence.

P0 entities:
    - person
    - location
    - date
    - operation
"""

import re

from backend.app.schemas.models import Entity, RetrievalResult


# ---------------------------------------------------------------------------
# REGEX PATTERNS
# ---------------------------------------------------------------------------

DATE_PATTERNS = [
    # March 15, 2026
    r"\b(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*|\s+)\d{4}\b",

    # 15 March 2026
    r"\b\d{1,2}(?:st|nd|rd|th)?\s+"
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"\s+\d{4}\b",

    # 2026-03-15
    r"\b\d{4}-\d{2}-\d{2}\b",
]


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _extract_dates(text: str) -> list[str]:
    """Extract dates from text."""

    dates: list[str] = []

    for pattern in DATE_PATTERNS:
        dates.extend(
            re.findall(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
        )

    return list(dict.fromkeys(dates))


def _extract_people(text: str) -> list[str]:
    """Extract simple Agent/person references."""

    people = re.findall(
        r"\bAgent\s+[A-Z][A-Za-z]+\b",
        text,
    )

    return list(dict.fromkeys(people))


def _extract_locations(text: str) -> list[str]:
    """Extract simple location references."""

    locations: list[str] = []

    # Sector 7, Sector 12, etc.
    locations.extend(
        re.findall(
            r"\bSector\s+\d+\b",
            text,
            flags=re.IGNORECASE,
        )
    )

    # Capitalized locations after at/in/near.
    locations.extend(
        re.findall(
            r"\b(?:at|in|near)\s+"
            r"([A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*){0,2})",
            text,
        )
    )

    return list(dict.fromkeys(locations))


def _extract_operations(text: str) -> list[str]:
    """
    Extract simple operation/event references.

    P0 intentionally uses deterministic phrase detection.
    """

    operations: list[str] = []

    # Explicit "operation" references.
    operations.extend(
        re.findall(
            r"\b[A-Za-z0-9_-]*operation[A-Za-z0-9_-]*\b",
            text,
            flags=re.IGNORECASE,
        )
    )

    # Common event wording.
    if re.search(
        r"\bthe operation\b",
        text,
        flags=re.IGNORECASE,
    ):
        operations.append("operation")

    return list(dict.fromkeys(operations))


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def extract_entities(
    retrieval_results: list[RetrievalResult],
) -> list[Entity]:
    """
    Extract and link entities across retrieval results.

    The same entity appearing in multiple sources is represented
    by one Entity with multiple source_ids.
    """

    entity_sources: dict[tuple[str, str], set[str]] = {}

    for result in retrieval_results:

        if not result.text.strip():
            continue

        source_id = result.source_id
        text = result.text

        # ---------------------------------------------------------
        # PERSON
        # ---------------------------------------------------------

        for name in _extract_people(text):
            key = ("person", name)

            entity_sources.setdefault(
                key,
                set(),
            ).add(source_id)

        # ---------------------------------------------------------
        # LOCATION
        # ---------------------------------------------------------

        for name in _extract_locations(text):
            key = ("location", name)

            entity_sources.setdefault(
                key,
                set(),
            ).add(source_id)

        # ---------------------------------------------------------
        # DATE
        # ---------------------------------------------------------

        for name in _extract_dates(text):
            key = ("date", name)

            entity_sources.setdefault(
                key,
                set(),
            ).add(source_id)

        # ---------------------------------------------------------
        # OPERATION
        # ---------------------------------------------------------

        for name in _extract_operations(text):
            key = ("operation", name)

            entity_sources.setdefault(
                key,
                set(),
            ).add(source_id)

    # -------------------------------------------------------------
    # Convert to API entities
    # -------------------------------------------------------------

    entities: list[Entity] = []

    for (entity_type, name), source_ids in entity_sources.items():

        entities.append(
            Entity(
                name=name,
                type=entity_type,
                source_ids=sorted(source_ids),
            )
        )

    return entities