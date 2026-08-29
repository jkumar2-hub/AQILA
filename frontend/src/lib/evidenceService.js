// AQILA Evidence Service
// Returns AQILAResponse.evidence (EvidenceGraph) from the mock for development.
//
// To wire the real backend (M4 integration), two paths are possible:
//   A) If the evidence comes from a prior query result already stored in state:
//      just pass AQILAResponse.evidence directly — no service call needed.
//   B) If fetching by query_id: replace this with GET /api/query/{id}/evidence.
//      Call sites (EvidencePage) need zero changes.
//
// EvidenceGraph shape (docs/API_CONTRACTS.md):
//   nodes: { id, label, modality, color, confidence }[]
//   edges: { source, target, edge_type, similarity, temporal_gap }[]

import mockData from '../mocks/mock_response.json'

/** Simulated delay — keeps the loading state visible */
const SIMULATED_DELAY_MS = 800

/**
 * Fetch the EvidenceGraph for demo/mock mode.
 *
 * @returns {Promise<{ nodes: GraphNode[], edges: GraphEdge[] }>}
 */
export async function fetchEvidenceGraph() {
  await new Promise((resolve) => setTimeout(resolve, SIMULATED_DELAY_MS))

  // Return only the documented EvidenceGraph fields
  const { nodes, edges } = mockData.evidence
  return { nodes, edges }
}
