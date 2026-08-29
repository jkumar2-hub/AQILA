"""
evidence/contradiction.py

AQILA — Contradiction Detection Module
Owner: M2 — Evidence Intelligence

P0:
    Two-stage contradiction detection.

    Stage 1:
        Deterministically find candidate conflicts involving:
        - dates
        - names
        - locations

    Stage 2:
        Use Ollama only for candidate pairs to verify
        whether the claims actually contradict each other.
"""

import re
from typing import Any

import requests

from backend.app.schemas.models import Contradiction, RetrievalResult


OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "llama3.2:3b"


# ---------------------------------------------------------------------------
# REGEX PATTERNS
# ---------------------------------------------------------------------------

DATE_PATTERNS = [
    # March 15, 2026
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*|\s+)\d{4}\b",

    # 15 March 2026
    r"\b\d{1,2}(?:st|nd|rd|th)?\s+"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{4}\b",

    # 2026-03-15
    r"\b\d{4}-\d{2}-\d{2}\b",
]


# ---------------------------------------------------------------------------
# EXTRACTION HELPERS
# ---------------------------------------------------------------------------

def _extract_dates(text: str) -> list[str]:
    """Extract date strings from text."""

    dates: list[str] = []

    for pattern in DATE_PATTERNS:
        dates.extend(
            re.findall(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
        )

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(dates))


def _extract_locations(text: str) -> list[str]:
    """
    Extract simple location references.

    P0 specifically needs locations such as:
        Sector 7
        Sector 12
        Delhi
        Mumbai
    """

    locations: list[str] = []

    # Sector 7, Sector 12, etc.
    locations.extend(
        re.findall(
            r"\bSector\s+\d+\b",
            text,
            flags=re.IGNORECASE,
        )
    )

    # Common "at/in <capitalized phrase>" locations.
    locations.extend(
        re.findall(
            r"\b(?:at|in|near)\s+"
            r"([A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*){0,2})",
            text,
        )
    )

    return list(dict.fromkeys(locations))


def _extract_names(text: str) -> list[str]:
    """
    Extract simple person/entity names.

    Example:
        Agent Mehra
        Agent Sharma
    """

    names = re.findall(
        r"\bAgent\s+([A-Z][A-Za-z]+)\b",
        text,
    )

    return list(dict.fromkeys(names))


def _topic_tokens(text: str) -> set[str]:
    """
    Extract meaningful lowercase words used to determine whether
    two claims are probably about the same topic/event.
    """

    stop_words = {
        "the",
        "was",
        "were",
        "is",
        "are",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "at",
        "for",
        "with",
        "from",
        "before",
        "after",
        "this",
        "that",
        "has",
        "have",
        "had",
        "been",
        "by",
        "as",
        "it",
    }

    words = re.findall(
        r"\b[a-zA-Z]{3,}\b",
        text.lower(),
    )

    return {
        word
        for word in words
        if word not in stop_words
    }


def _same_topic(text_a: str, text_b: str) -> bool:
    """
    Determine whether two claims have enough shared vocabulary
    to be considered the same topic/event.
    """

    tokens_a = _topic_tokens(text_a)
    tokens_b = _topic_tokens(text_b)

    if not tokens_a or not tokens_b:
        return False

    overlap = tokens_a & tokens_b

    # One shared meaningful event token is enough for the P0
    # deterministic candidate stage.
    return bool(overlap)


# ---------------------------------------------------------------------------
# STAGE 1 — DETERMINISTIC CANDIDATE DETECTION
# ---------------------------------------------------------------------------

def _candidate_pairs(
    retrieval_results: list[RetrievalResult],
) -> list[dict[str, Any]]:
    """
    Find candidate contradiction pairs without using an LLM.

    Candidate types:
        date
        name
        location
    """

    candidates: list[dict[str, Any]] = []

    for i in range(len(retrieval_results)):
        result_a = retrieval_results[i]

        if not result_a.text.strip():
            continue

        for j in range(i + 1, len(retrieval_results)):
            result_b = retrieval_results[j]

            if not result_b.text.strip():
                continue

            # Same chunk/source is not a contradiction candidate.
            if result_a.source_id == result_b.source_id:
                continue

            if not _same_topic(result_a.text, result_b.text):
                continue

            # ---------------------------------------------------------
            # DATE CONFLICT
            # ---------------------------------------------------------

            dates_a = _extract_dates(result_a.text)
            dates_b = _extract_dates(result_b.text)

            if dates_a and dates_b:
                if set(dates_a) != set(dates_b):
                    candidates.append(
                        {
                            "claim_a": result_a.text,
                            "claim_b": result_b.text,
                            "source_a": result_a.source_id,
                            "source_b": result_b.source_id,
                            "conflict_type": "date",
                        }
                    )
                    continue

            # ---------------------------------------------------------
            # NAME CONFLICT
            # ---------------------------------------------------------

            names_a = _extract_names(result_a.text)
            names_b = _extract_names(result_b.text)

            if names_a and names_b:
                if set(names_a) != set(names_b):
                    candidates.append(
                        {
                            "claim_a": result_a.text,
                            "claim_b": result_b.text,
                            "source_a": result_a.source_id,
                            "source_b": result_b.source_id,
                            "conflict_type": "name",
                        }
                    )
                    continue

            # ---------------------------------------------------------
            # LOCATION CONFLICT
            # ---------------------------------------------------------

            locations_a = _extract_locations(result_a.text)
            locations_b = _extract_locations(result_b.text)

            if locations_a and locations_b:
                if set(locations_a) != set(locations_b):
                    candidates.append(
                        {
                            "claim_a": result_a.text,
                            "claim_b": result_b.text,
                            "source_a": result_a.source_id,
                            "source_b": result_b.source_id,
                            "conflict_type": "location",
                        }
                    )

    return candidates


# ---------------------------------------------------------------------------
# STAGE 2 — LLM VERIFICATION
# ---------------------------------------------------------------------------

def _build_verification_prompt(candidate: dict) -> str:
    """
    Build a strict contradiction-verification prompt.

    The deterministic stage has already identified a likely conflict.
    Ollama only decides whether the two claims actually contradict.
    """

    return f"""
You are a strict contradiction detector.

Two independent sources make claims about the SAME event.

SOURCE A CLAIM:
{candidate["claim_a"]}

SOURCE B CLAIM:
{candidate["claim_b"]}

CONFLICT TYPE:
{candidate["conflict_type"]}

Determine whether the claims contradict each other.

IMPORTANT RULES:

1. If SOURCE A says an event happened on one date and
   SOURCE B says the same event happened on a different date,
   this IS a contradiction.

2. If SOURCE A gives one location and SOURCE B gives a different
   location for the same event, this IS a contradiction.

3. If SOURCE A identifies one person and SOURCE B identifies a
   different person for the same role/event, this IS a contradiction.

4. Do not reject a contradiction merely because the rest of the
   claims are similar.

5. Do not invent facts.

For this candidate, the deterministic system has already identified
the conflict type. Your job is ONLY to verify whether the conflicting
values are genuinely different.

Return EXACTLY one of these formats:

YES
CLAIM_A: <claim from source A>
CLAIM_B: <claim from source B>

OR

NO

Do not return JSON.
Do not explain your answer.
Do not add any other text.

ANSWER:
""".strip()

def _call_ollama(prompt: str) -> str:
    """Call the local Ollama server."""

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
            },
        },
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    return str(data.get("response", "")).strip()


def _verify_candidate(
    candidate: dict[str, Any],
) -> Contradiction | None:
    """Ask Ollama to verify one deterministic candidate."""

    prompt = _build_verification_prompt(candidate)

    try:
        response = _call_ollama(prompt)
    except Exception as exc:
        print(
            f"[AQILA] Contradiction verification failed: {exc}"
        )
        return None

    if not re.search(
        r"\bYES\b",
        response,
        flags=re.IGNORECASE,
    ):
        return None

    # Try to extract the model's normalized claims.
    claim_a_match = re.search(
        r"CLAIM_A:\s*(.+)",
        response,
        flags=re.IGNORECASE,
    )

    claim_b_match = re.search(
        r"CLAIM_B:\s*(.+)",
        response,
        flags=re.IGNORECASE,
    )

    claim_a = (
        claim_a_match.group(1).strip()
        if claim_a_match
        else candidate["claim_a"]
    )

    claim_b = (
        claim_b_match.group(1).strip()
        if claim_b_match
        else candidate["claim_b"]
    )

    return Contradiction(
        claim_a=claim_a,
        claim_b=claim_b,
        source_a=candidate["source_a"],
        source_b=candidate["source_b"],
        conflict_type=candidate["conflict_type"],
        confidence=1.0,
    )


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def detect_contradiction(
    retrieval_results: list[RetrievalResult],
) -> Contradiction | None:
    """
    Detect the first verified contradiction.

    Stage 1:
        deterministic candidate generation.

    Stage 2:
        LLM verification only for candidates.

    Returns:
        Contradiction object if verified.
        None otherwise.
    """

    if not retrieval_results:
        return None

    candidates = _candidate_pairs(retrieval_results)

    if not candidates:
        return None

    for candidate in candidates:
        contradiction = _verify_candidate(candidate)

        if contradiction is not None:
            return contradiction

    return None