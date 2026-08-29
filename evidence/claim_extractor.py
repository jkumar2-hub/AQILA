"""
AQILA — Claim Extraction Module

Owner: M2 — Evidence Intelligence

Extracts factual claims from retrieved text using Ollama.
"""

import json
import re
from typing import Any

import requests

from backend.app.schemas.models import Claim, RetrievalResult


OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "llama3.2:3b"


# ---------------------------------------------------------------------------
# PROMPT
# ---------------------------------------------------------------------------

def _build_prompt(text: str) -> str:
    """
    Build a strict factual claim extraction prompt.
    """

    return f"""
You are an evidence extraction system.

Extract EVERY important factual claim explicitly stated in the source.

This is extremely important:
- Do NOT skip dates.
- Do NOT skip names.
- Do NOT skip locations.
- Do NOT skip operation/event facts.
- Preserve exact dates and names from the source.
- Extract conflicting facts even if they seem similar.
- Do not combine unrelated facts into one claim.
- Do not invent or infer information.

Examples of claims that MUST be extracted:
- "The operation was conducted on March 15, 2026."
- "Agent Mehra was present."
- "The operation occurred in Sector 7."

Return ONLY valid JSON.

Return a JSON array.

Each item MUST contain:
"text": concise factual claim copied or faithfully summarized from the source
"confidence": number between 0 and 1

SOURCE TEXT:
{text}

JSON:
""".strip()


# ---------------------------------------------------------------------------
# OLLAMA
# ---------------------------------------------------------------------------

def _call_ollama(prompt: str) -> str:
    """
    Call the local Ollama server.
    """

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
    	     "model": OLLAMA_MODEL,
             "prompt": prompt,
             "stream": False,
             "format": "json",
             "options": {
                "temperature": 0.1,
             },
          },
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("response", "")


# ---------------------------------------------------------------------------
# JSON PARSING
# ---------------------------------------------------------------------------

def _parse_claim_json(
    response_text: str,
) -> list[dict[str, Any]]:
    """
    Parse Ollama JSON output robustly.

    Supports:
        1. JSON array of claims
        2. Single claim object
        3. {"claims": [...]} wrapper
        4. Markdown JSON code fences
    """

    text = response_text.strip()

    # Remove markdown code fences if the model adds them.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    try:
        parsed = json.loads(text)

    except json.JSONDecodeError:

        # Try extracting a JSON array.
        match = re.search(
            r"\[.*\]",
            text,
            flags=re.DOTALL,
        )

        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                return []

        else:
            # Try extracting a single JSON object.
            match = re.search(
                r"\{.*\}",
                text,
                flags=re.DOTALL,
            )

            if not match:
                return []

            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                return []

    # ---------------------------------------------------------
    # Normalize different valid response shapes
    # ---------------------------------------------------------

    # Normal expected format:
    #
    # [
    #     {"text": "...", "confidence": 0.9}
    # ]
    if isinstance(parsed, list):
        return [
            item
            for item in parsed
            if isinstance(item, dict)
        ]

    # Wrapped format:
    #
    # {
    #     "claims": [
    #         {"text": "...", "confidence": 0.9}
    #     ]
    # }
    if isinstance(parsed, dict):
        claims = parsed.get("claims")

        if isinstance(claims, list):
            return [
                item
                for item in claims
                if isinstance(item, dict)
            ]

        # Single claim format returned by Ollama:
        #
        # {
        #     "text": "...",
        #     "confidence": 1.0
        # }
        if "text" in parsed:
            return [parsed]

    return []


# ---------------------------------------------------------------------------
# CLAIM EXTRACTION
# ---------------------------------------------------------------------------

def extract_claims(
    retrieval_results: list[RetrievalResult],
) -> list[Claim]:
    """
    Extract factual claims from retrieved chunks.

    Each retrieval result is processed independently.
    """

    claims: list[Claim] = []

    for result in retrieval_results:

        if not result.text.strip():
            continue

        prompt = _build_prompt(result.text)

        try:
            raw_response = _call_ollama(prompt)

        except Exception as exc:
            print(
                f"[AQILA] Claim extraction failed "
                f"for {result.source_id}: {exc}"
            )
            continue

        extracted = _parse_claim_json(raw_response)

        for item in extracted:

            claim_text = str(
                item.get("text", "")
            ).strip()

            if not claim_text:
                continue

            try:
                confidence = float(
                    item.get("confidence", 0.5)
                )
            except (TypeError, ValueError):
                confidence = 0.5

            # Keep confidence inside API contract.
            confidence = max(
                0.0,
                min(1.0, confidence),
            )

            claims.append(
                Claim(
                    text=claim_text,
                    source_id=result.source_id,
                    confidence=confidence,
                )
            )

    return claims