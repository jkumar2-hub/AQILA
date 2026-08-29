"""
AQILA — Evidence Intelligence Engine

Owner: M2 — Evidence Intelligence

Orchestrates the P0 evidence pipeline:

    RetrievalResult[]
        ↓
    Claim extraction
        ↓
    Entity extraction/linking
        ↓
    Contradiction detection
        ↓
    Evidence graph construction
        ↓
    EvidenceResult
"""

from backend.app.schemas.models import (
    EvidenceResult,
    Relationship,
    RetrievalResult,
)

from .claim_extractor import extract_claims
from .contradiction import detect_contradiction
from .entity_linker import extract_entities
from .graph_builder import build_evidence_graph


# ---------------------------------------------------------------------------
# RELATIONSHIPS
# ---------------------------------------------------------------------------

def _build_relationships(
    entities,
) -> list[Relationship]:
    """
    Build simple source-to-source relationships from shared entities.

    P0 relationship rule:
        If the same entity occurs in multiple sources,
        those sources are related through that entity.

    More advanced relationship types are P1 work.
    """

    relationships: list[Relationship] = []

    seen: set[tuple[str, str, str]] = set()

    for entity in entities:

        source_ids = sorted(set(entity.source_ids))

        if len(source_ids) < 2:
            continue

        for i in range(len(source_ids)):
            for j in range(i + 1, len(source_ids)):

                source_a = source_ids[i]
                source_b = source_ids[j]

                key = (
                    source_a,
                    source_b,
                    entity.type,
                )

                if key in seen:
                    continue

                seen.add(key)

                relationships.append(
                    Relationship(
                        source_a=source_a,
                        source_b=source_b,
                        type=f"shared_{entity.type}",
                        confidence=1.0,
                    )
                )

    return relationships


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def build_evidence(
    retrieval_results: list[RetrievalResult],
) -> EvidenceResult:
    """
    Run the complete M2 P0 evidence pipeline.

    Parameters
    ----------
    retrieval_results:
        Results returned by M1 retrieval.

    Returns
    -------
    EvidenceResult
        Evidence package consumed by M4.
    """

    # ---------------------------------------------------------
    # Empty retrieval
    # ---------------------------------------------------------

    if not retrieval_results:
        return EvidenceResult(
            claims=[],
            entities=[],
            relationships=[],
            temporal_links=[],
            contradictions=[],
            graph=build_evidence_graph([]),
            source_references=[],
        )

    # ---------------------------------------------------------
    # 1. Claim extraction
    # ---------------------------------------------------------

    claims = extract_claims(
        retrieval_results
    )

    # ---------------------------------------------------------
    # 2. Entity extraction / linking
    # ---------------------------------------------------------

    entities = extract_entities(
        retrieval_results
    )

    # ---------------------------------------------------------
    # 3. Relationships
    # ---------------------------------------------------------

    relationships = _build_relationships(
        entities
    )

    # ---------------------------------------------------------
    # 4. Contradiction detection
    #
    # P0 detector currently returns the first
    # verified contradiction.
    # ---------------------------------------------------------

    contradiction = detect_contradiction(
        retrieval_results
    )

    contradictions = []

    if contradiction is not None:
        contradictions.append(
            contradiction
        )

    # ---------------------------------------------------------
    # 5. Evidence graph
    # ---------------------------------------------------------

    graph = build_evidence_graph(
        retrieval_results
    )

    # ---------------------------------------------------------
    # 6. Source references
    # ---------------------------------------------------------

    source_references = list(
        dict.fromkeys(
            result.source_id
            for result in retrieval_results
        )
    )

    # ---------------------------------------------------------
    # 7. Assemble frozen API contract
    # ---------------------------------------------------------

    return EvidenceResult(
        claims=claims,
        entities=entities,
        relationships=relationships,
        temporal_links=[],
        contradictions=contradictions,
        graph=graph,
        source_references=source_references,
    )