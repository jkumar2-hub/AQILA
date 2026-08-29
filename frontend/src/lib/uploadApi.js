// AQILA Upload API — pure fetch functions, no React
// Source of truth: docs/API_CONTRACTS.md §API Endpoints
// Only documented response fields are consumed.

import { ENDPOINTS } from './constants'

/**
 * Upload a single file to POST /api/ingest/upload.
 * Uses multipart/form-data with field name "file".
 *
 * @param {File} file
 * @returns {Promise<{ source_id: string, status: string }>}
 * @throws {Error} on network failure or non-2xx response
 */
export async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  // Do NOT manually set Content-Type — the browser sets it with
  // the correct multipart boundary automatically.

  const response = await fetch(ENDPOINTS.ingestUpload, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    let message = `Upload failed (${response.status} ${response.statusText})`
    try {
      const body = await response.json()
      if (body?.detail) message = String(body.detail)
    } catch (_) {
      // non-JSON error body — use status text
    }
    throw new Error(message)
  }

  const data = await response.json()
  // Consume only documented fields: source_id, status
  return { source_id: data.source_id, status: data.status }
}

/**
 * Fetch the current ingest status for a source.
 * GET /api/ingest/status/{source_id}
 *
 * @param {string} sourceId
 * @returns {Promise<{ status: string }>}   status: 'processing' | 'indexed' | 'failed'
 * @throws {Error} on network failure or non-2xx response
 */
export async function fetchIngestStatus(sourceId) {
  const response = await fetch(ENDPOINTS.ingestStatus(sourceId))

  if (!response.ok) {
    throw new Error(`Status check failed (${response.status} ${response.statusText})`)
  }

  const data = await response.json()
  // Consume only documented field: status
  return { status: data.status }
}
