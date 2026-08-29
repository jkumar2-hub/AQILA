// AQILA Query Service
// Currently returns mock_response.json after a simulated delay.
// Shape matches AQILAResponse exactly per docs/API_CONTRACTS.md.
//
// To wire the real backend (M4 integration):
//   Replace the mock body with a real fetch to ENDPOINTS.query.
//   The call sites (QueryPage) need zero changes.

import mockData from '../mocks/mock_response.json'

/** Simulated network delay in ms — makes the loading state visible for demo */
const SIMULATED_DELAY_MS = 1500

/**
 * Run a query against the AQILA knowledge base.
 *
 * @param {string} _queryText — the user's question (used by real API; ignored by mock)
 * @returns {Promise<{
 *   query_id: string,
 *   answer: string,
 *   citations: Citation[],
 *   contradiction_found: boolean,
 *   contradiction_detail: Contradiction | null,
 *   evidence: EvidenceGraph,
 *   sources: SourceSummary[],
 *   response_time_ms: number,
 * }>}
 */
export async function runQuery(_queryText) {
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_DELAY_MS))

  // Destructure only documented AQILAResponse fields — strips _comment, _purpose, etc.
  const {
    query_id,
    answer,
    citations,
    contradiction_found,
    contradiction_detail,
    evidence,
    sources,
    response_time_ms,
  } = mockData

  return {
    query_id,
    answer,
    citations,
    contradiction_found,
    contradiction_detail,
    evidence,
    sources,
    response_time_ms,
  }
}
