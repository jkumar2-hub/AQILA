"""
AQILA — Evidence Chain Graph Builder

Owner: M2 — Evidence Intelligence

Builds a semantic evidence graph from RetrievalResult objects.

Rules:
    - Use existing embeddings from RetrievalResult.
    - Never recompute embeddings.
    - Only compare embeddings from the same embedding space.
    - Skip missing embeddings.
    - Semantic edge threshold: cosine similarity > 0.6.
"""

from itertools import combinations
from typing import Any

import networkx as nx

from backend.app.schemas.models import (
    EvidenceGraph,
    GraphEdge,
    GraphNode,
    RetrievalResult,
)


# ---------------------------------------------------------------------------
# MODALITY COLORS
# ---------------------------------------------------------------------------

MODALITY_COLORS = {
    "text": "#1D9E75",
    "audio": "#EF9F27",
    "image": "#534AB7",
}


# ---------------------------------------------------------------------------
# COSINE SIMILARITY
# ---------------------------------------------------------------------------

def cosine_similarity(
    a: list[float],
    b: list[float],
) -> float:
    """
    Calculate cosine similarity between two vectors.
    """

    if not a or not b:
        return 0.0

    if len(a) != len(b):
        raise ValueError(
            "Cannot compare embeddings with different dimensions"
        )

    dot_product = sum(x * y for x, y in zip(a, b))

    magnitude_a = sum(x * x for x in a) ** 0.5
    magnitude_b = sum(y * y for y in b) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


# ---------------------------------------------------------------------------
# EVIDENCE GRAPH
# ---------------------------------------------------------------------------

def build_evidence_graph(
    retrieval_results: list[RetrievalResult],
) -> EvidenceGraph:
    """
    Build semantic evidence graph from retrieved chunks.

    P0:
        - One graph node per source_id.
        - Compare chunk embeddings pairwise.
        - Same embedding space only.
        - cosine similarity > 0.6 creates semantic edge.
        - Multiple chunks between the same sources are reduced
          to the strongest semantic relationship.
    """

    graph = nx.Graph()

    # ---------------------------------------------------------
    # Add one node per source
    # ---------------------------------------------------------

    source_results: dict[str, RetrievalResult] = {}

    for result in retrieval_results:
        if result.source_id not in source_results:
            source_results[result.source_id] = result

            graph.add_node(
                result.source_id,
                label=result.file_name,
                modality=result.modality,
                color=MODALITY_COLORS.get(
                    result.modality,
                    "#1D9E75",
                ),
                confidence=result.score,
            )

    # ---------------------------------------------------------
    # Compare retrieval results pairwise
    # ---------------------------------------------------------

    for result_a, result_b in combinations(
        retrieval_results,
        2,
    ):

        # -----------------------------------------------------
        # REQUIRED: embeddings must exist
        # -----------------------------------------------------

        if result_a.embedding is None:
            continue

        if result_b.embedding is None:
            continue

        # -----------------------------------------------------
        # REQUIRED: embedding spaces must exist
        # -----------------------------------------------------

        if result_a.embedding_space is None:
            continue

        if result_b.embedding_space is None:
            continue

        # -----------------------------------------------------
        # CRITICAL SAME-SPACE GUARD
        # -----------------------------------------------------

        if result_a.embedding_space != result_b.embedding_space:
            continue

        # -----------------------------------------------------
        # Calculate pairwise cosine similarity
        # -----------------------------------------------------

        similarity = cosine_similarity(
            result_a.embedding,
            result_b.embedding,
        )

        # -----------------------------------------------------
        # Semantic edge threshold
        # -----------------------------------------------------

        if similarity <= 0.6:
            continue

        source_a = result_a.source_id
        source_b = result_b.source_id

        # Same source does not create an evidence relationship.
        if source_a == source_b:
            continue

        # -----------------------------------------------------
        # Keep strongest edge between two sources
        # -----------------------------------------------------

        if graph.has_edge(source_a, source_b):

            existing = graph[source_a][source_b]["similarity"]

            if similarity > existing:
                graph[source_a][source_b]["similarity"] = similarity

        else:

            graph.add_edge(
                source_a,
                source_b,
                edge_type="semantic",
                similarity=similarity,
            )

    # ---------------------------------------------------------
    # Convert NetworkX graph → API contract
    # ---------------------------------------------------------

    nodes: list[GraphNode] = []

    for node_id, data in graph.nodes(data=True):

        nodes.append(
            GraphNode(
                id=node_id,
                label=data["label"],
                modality=data["modality"],
                color=data["color"],
                confidence=data["confidence"],
            )
        )

    edges: list[GraphEdge] = []

    for source, target, data in graph.edges(data=True):

        edges.append(
            GraphEdge(
                source=source,
                target=target,
                edge_type="semantic",
                similarity=float(data["similarity"]),
                temporal_gap=None,
            )
        )

    return EvidenceGraph(
        nodes=nodes,
        edges=edges,
    )