// AQILA frontend constants
// Source of truth: docs/API_CONTRACTS.md

/** Base URL for API calls. Vite proxy rewrites /api/* → http://localhost:8000 */
export const API_BASE = '/api'

/** Modality colour map — matches API_CONTRACTS.md §Node Colour Reference */
export const MODALITY_COLORS = {
  text:  '#1D9E75', // teal  — Document (PDF/DOCX)
  audio: '#EF9F27', // amber — Audio
  image: '#534AB7', // purple — Image
}

/** Ingest status values */
export const INGEST_STATUS = {
  PROCESSING: 'processing',
  INDEXED:    'indexed',
  FAILED:     'failed',
}

/** API endpoint paths */
export const ENDPOINTS = {
  ingestUpload:  `${API_BASE}/ingest/upload`,
  ingestStatus:  (sourceId) => `${API_BASE}/ingest/status/${sourceId}`,
  query:         `${API_BASE}/query`,
  queryEvidence: (queryId) => `${API_BASE}/query/${queryId}/evidence`,
  sources:       `${API_BASE}/sources`,          // P1
  deleteSource:  (sourceId) => `${API_BASE}/sources/${sourceId}`, // P1
  settings:      `${API_BASE}/settings/status`,  // P1
}
