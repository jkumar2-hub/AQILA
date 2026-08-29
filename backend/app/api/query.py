"""

AQILA â€” Query API Router



Owner: M4 â€” Backend / Platform / Integration



P0 endpoints:

    POST /api/query

    GET  /api/query/{query_id}/evidence



Pipeline:

    QueryRequest

        â†’ M1: retrieve_text_p0(query, top_k=8)

        â†’ M2: build_evidence(retrieval_results)

        â†’ M1: generate_answer(query, retrieval_results)

        â†’ M4: assemble AQILAResponse (strips embedding/embedding_space)

        â†’ persist Query + EvidenceEdges to SQLite

        â†’ return AQILAResponse

"""



import json

import time

from datetime import datetime, timezone

from uuid import uuid4



from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession



from ..db.database import AsyncSessionLocal, get_db

from ..db.models import EvidenceEdge, Query, Source

from ..schemas.models import (

    AQILAResponse,

    Citation,

    EvidenceGraph,

    QueryRequest,

    SourceSummary,

)





router = APIRouter(

    prefix="/api/query",

    tags=["query"],

)





# ---------------------------------------------------------------------------

# Helpers â€” lazy imports of M1 / M2 to avoid import-time side effects

# ---------------------------------------------------------------------------



def _get_retriever():

    from rag.retriever import retrieve_text_p0, retrieve_audio_p1

    return retrieve_text_p0, retrieve_audio_p1





def _get_evidence_engine():

    from evidence.engine import build_evidence

    return build_evidence





def _get_generator():

    from rag.generator import generate_answer

    return generate_answer





# ---------------------------------------------------------------------------

# Citation builder

# ---------------------------------------------------------------------------



def _build_citations(

    retrieval_results,

    answer: str,

) -> list[Citation]:

    """

    Build Citation objects matching [N] markers in the LLM answer.



    Only citations that appear in the answer as [N] are included.

    Citation numbers are 1-indexed to match the [N] format in the

    grounded prompt built by M1's generator.

    """

    import re



    cited_numbers = {

        int(m) for m in re.findall(r"\[(\d+)\]", answer)

    }



    citations: list[Citation] = []

    for idx, result in enumerate(retrieval_results, start=1):

        if idx not in cited_numbers:

            continue



        snippet = (result.text or "").strip()

        if len(snippet) > 200:

            snippet = snippet[:200].rstrip() + "..."



        citations.append(

            Citation(

                num=idx,

                source_id=result.source_id,

                source_name=result.file_name,

                modality=result.modality,

                page=result.page_number,

                timestamp_start=result.timestamp_start,

                timestamp_end=result.timestamp_end,

                text=snippet,

            )

        )



    return citations





# ---------------------------------------------------------------------------

# Source summary builder

# ---------------------------------------------------------------------------



async def _build_source_summaries(

    retrieval_results,

    db: AsyncSession,

) -> list[SourceSummary]:

    """

    Build SourceSummary list from retrieved results, enriching

    with chunk_count and status from SQLite where available.

    """

    seen_ids: dict[str, SourceSummary] = {}



    for result in retrieval_results:

        if result.source_id in seen_ids:

            continue



        # Try to fetch real status from DB.

        row = await db.get(Source, result.source_id)



        seen_ids[result.source_id] = SourceSummary(

            source_id=result.source_id,

            file_name=result.file_name,

            modality=result.modality,

            chunk_count=row.chunk_count if row and row.chunk_count else 1,

            status=row.status if row and row.status else "indexed",

        )



    return list(seen_ids.values())





# ---------------------------------------------------------------------------

# Evidence persistence

# ---------------------------------------------------------------------------



async def _persist_evidence(

    query_id: str,

    evidence_graph: EvidenceGraph,

) -> None:

    """

    Persist evidence graph edges to SQLite for GET /evidence retrieval.

    Each edge is stored as a row in the evidence_edges table.

    """

    async with AsyncSessionLocal() as session:

        for edge in evidence_graph.edges:

            edge_id = str(uuid4())

            row = EvidenceEdge(

                edge_id=edge_id,

                query_id=query_id,

                source_a=edge.source,

                source_b=edge.target,

                edge_type=edge.edge_type,

                similarity=edge.similarity,

                temporal_gap=edge.temporal_gap,

            )

            session.add(row)

        await session.commit()





# ---------------------------------------------------------------------------

# POST /api/query

# ---------------------------------------------------------------------------



@router.post(

    "",

    response_model=AQILAResponse,

    summary="Run AQILA RAG + evidence pipeline",

)

async def run_query(

    request: QueryRequest,

    db: AsyncSession = Depends(get_db),

) -> AQILAResponse:

    """

    Full M1 â†’ M2 â†’ M4 pipeline.



    1. M1: retrieve_text_p0(query, top_k=8)

    2. M2: build_evidence(retrieval_results)

    3. M1: generate_answer(query, retrieval_results)

    4. M4: build citations, source summaries, AQILAResponse

           (embedding and embedding_space are NEVER included in AQILAResponse)

    5. Persist Query record and EvidenceEdges to SQLite.

    """



    if not request.query or not request.query.strip():

        raise HTTPException(status_code=422, detail="query must not be empty")



    query_id = str(uuid4())

    start_ms = time.monotonic()



    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
# 1. M1 ? Retrieval
    # ------------------------------------------------------------------
    try:
        retrieve_text_p0, retrieve_audio_p1 = _get_retriever()

        retrieval_results = (
            retrieve_text_p0(request.query, top_k=8)
            + retrieve_audio_p1(request.query, top_k=4)
        )

        # Keep strongest evidence first so the grounded LLM
        # sees the most relevant chunks at the lowest citation numbers.
        retrieval_results = sorted(
            retrieval_results,
            key=lambda r: getattr(r, "score", 0.0),
            reverse=True,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"M1 retrieval failed: {exc}",
        ) from exc

    # ------------------------------------------------------------------
    # 2. M2 — Evidence intelligence â€” Evidence intelligence

    # ------------------------------------------------------------------

    try:

        build_evidence = _get_evidence_engine()

        evidence_result = build_evidence(retrieval_results)

    except Exception as exc:

        raise HTTPException(

            status_code=502,

            detail=f"M2 evidence pipeline failed: {exc}",

        ) from exc



    # ------------------------------------------------------------------

    # 3. M1 â€” Grounded generation

    # ------------------------------------------------------------------

    try:

        generate_answer = _get_generator()

        answer, _citation_dicts = generate_answer(

            query=request.query,

            retrieval_results=retrieval_results,

        )

    except Exception as exc:

        # Degrade gracefully â€” answer with evidence summary if LLM fails

        answer = (

            "Insufficient evidence to determine this. "

            f"(Generation failed: {exc})"

        )



    # ------------------------------------------------------------------

    # 4. M4 â€” Assemble AQILAResponse

    #    IMPORTANT: embedding and embedding_space MUST NOT appear here.

    # ------------------------------------------------------------------



    contradiction_found = bool(evidence_result.contradictions)

    contradiction_detail = (

        evidence_result.contradictions[0]

        if contradiction_found

        else None

    )



    citations = _build_citations(retrieval_results, answer)



    source_summaries = await _build_source_summaries(retrieval_results, db)



    elapsed_ms = int((time.monotonic() - start_ms) * 1000)



    response = AQILAResponse(

        query_id=query_id,

        answer=answer,

        citations=citations,

        contradiction_found=contradiction_found,

        contradiction_detail=contradiction_detail,

        evidence=evidence_result.graph,

        sources=source_summaries,

        response_time_ms=elapsed_ms,

    )



    # ------------------------------------------------------------------

    # 5. Persist Query record to SQLite

    # ------------------------------------------------------------------

    now = datetime.now(timezone.utc).isoformat()



    query_row = Query(

        query_id=query_id,

        query_text=request.query,

        answer=answer,

        response_time_ms=elapsed_ms,

        contradiction_found=int(contradiction_found),

        created_at=now,

    )

    db.add(query_row)

    await db.commit()



    # Persist evidence edges (fire and forget style â€” async, own session)

    try:

        await _persist_evidence(query_id, evidence_result.graph)

    except Exception:

        # Non-critical: log but do not fail the request

        pass



    return response





# ---------------------------------------------------------------------------

# GET /api/query/{query_id}/evidence

# ---------------------------------------------------------------------------



@router.get(

    "/{query_id}/evidence",

    response_model=EvidenceGraph,

    summary="Return the evidence graph for a past query",

)

async def get_query_evidence(

    query_id: str,

    db: AsyncSession = Depends(get_db),

) -> EvidenceGraph:

    """

    Retrieve the persisted EvidenceGraph for a completed query.



    Evidence edges are stored in the evidence_edges table, one row

    per edge. Nodes are reconstructed from the Source table using

    the source_a / source_b references.

    """



    # Verify the query exists.

    query_row = await db.get(Query, query_id)

    if query_row is None:

        raise HTTPException(

            status_code=404,

            detail=f"Query '{query_id}' not found.",

        )



    # Fetch edges for this query.

    result = await db.execute(

        select(EvidenceEdge).where(EvidenceEdge.query_id == query_id)

    )

    edge_rows = result.scalars().all()



    # Collect unique source IDs from edges.

    source_ids: set[str] = set()

    for edge_row in edge_rows:

        if edge_row.source_a:

            source_ids.add(edge_row.source_a)

        if edge_row.source_b:

            source_ids.add(edge_row.source_b)



    # Build nodes from Source table.

    from ..schemas.models import GraphEdge, GraphNode



    MODALITY_COLORS = {

        "text": "#1D9E75",

        "audio": "#EF9F27",

        "image": "#534AB7",

    }



    nodes: list[GraphNode] = []

    for sid in source_ids:

        src = await db.get(Source, sid)

        if src:

            modality = src.modality or "text"

            nodes.append(

                GraphNode(

                    id=sid,

                    label=src.file_name,

                    modality=modality,

                    color=MODALITY_COLORS.get(modality, "#1D9E75"),

                    confidence=1.0,

                )

            )



    # Build edges.

    edges: list[GraphEdge] = []

    for edge_row in edge_rows:

        if edge_row.source_a and edge_row.source_b:

            edges.append(

                GraphEdge(

                    source=edge_row.source_a,

                    target=edge_row.source_b,

                    edge_type=edge_row.edge_type or "semantic",

                    similarity=float(edge_row.similarity or 0.0),

                    temporal_gap=edge_row.temporal_gap,

                )

            )



    return EvidenceGraph(nodes=nodes, edges=edges)



