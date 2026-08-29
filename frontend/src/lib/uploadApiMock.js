// AQILA Upload API — Mock implementation for dev/demo use only.
//
// This file is NEVER imported in production.
// The selector (uploadService.js) imports this only when
// import.meta.env.VITE_DEMO_MODE === 'true', which Vite
// tree-shakes out of production bundles.
//
// Simulated lifecycle per file:
//   mockUploadFile()       → waits UPLOAD_DELAY_MS → resolves with { source_id, status:'processing' }
//   mockFetchIngestStatus() → returns 'processing' for PROCESSING_POLLS calls, then 'indexed'
//                           → every FAIL_EVERY_N-th upload resolves as 'failed' instead
//
// Real API contract (docs/API_CONTRACTS.md) is respected:
//   uploadFile returns    { source_id: string, status: string }
//   fetchStatus returns   { status: string }   ('processing' | 'indexed' | 'failed')

// ── Configuration ─────────────────────────────────────────────────────────

/** ms to simulate the network round-trip for the upload POST */
const UPLOAD_DELAY_MS = 900

/** ms to simulate each status poll */
const STATUS_POLL_DELAY_MS = 200

/** Number of 'processing' polls before resolving to a terminal state */
const PROCESSING_POLLS = 3

/**
 * Every N-th upload (1-based count) is marked as a failure.
 * Set to 0 to never fail, or 2 to fail every other upload.
 * Default: 4 (every 4th file will eventually show Failed + Retry)
 */
const FAIL_EVERY_N = 4

// ── Internal state ─────────────────────────────────────────────────────────

/** Counts how many times each demo sourceId has been polled */
const _pollCounts = new Map()

/** Running count of mock uploads — used to decide which ones fail */
let _uploadCounter = 0

// ── Helpers ────────────────────────────────────────────────────────────────

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function shortUUID() {
  return crypto.randomUUID().replace(/-/g, '').slice(0, 12)
}

// ── Mock functions ─────────────────────────────────────────────────────────

/**
 * Simulates POST /api/ingest/upload.
 * Waits UPLOAD_DELAY_MS then resolves with a demo source_id.
 *
 * @param {File} _file  (not used — we generate a fake source_id)
 * @returns {Promise<{ source_id: string, status: string }>}
 */
export async function mockUploadFile(_file) {
  await delay(UPLOAD_DELAY_MS)

  _uploadCounter++
  const willFail = FAIL_EVERY_N > 0 && _uploadCounter % FAIL_EVERY_N === 0
  // Encode outcome in the source_id prefix so the status poller can read it
  const prefix = willFail ? 'demo-fail' : 'demo-ok'
  const source_id = `${prefix}-${shortUUID()}`

  return { source_id, status: 'processing' }
}

/**
 * Simulates GET /api/ingest/status/{sourceId}.
 * Returns 'processing' for PROCESSING_POLLS calls, then the terminal state.
 *
 * @param {string} sourceId
 * @returns {Promise<{ status: string }>}
 */
export async function mockFetchIngestStatus(sourceId) {
  await delay(STATUS_POLL_DELAY_MS)

  const count = (_pollCounts.get(sourceId) ?? 0) + 1
  _pollCounts.set(sourceId, count)

  if (count >= PROCESSING_POLLS) {
    // Reached terminal state — clean up and resolve
    _pollCounts.delete(sourceId)
    const willFail = sourceId.startsWith('demo-fail')
    return { status: willFail ? 'failed' : 'indexed' }
  }

  return { status: 'processing' }
}
