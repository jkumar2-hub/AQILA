// AQILA Upload Service — compile-time selector between real and mock API.
//
// When VITE_DEMO_MODE === 'true' (set in .env.development.local):
//   → uses mockUploadFile / mockFetchIngestStatus from uploadApiMock.js
//
// Otherwise (production or dev without the env var):
//   → uses real uploadFile / fetchIngestStatus from uploadApi.js
//
// Vite evaluates import.meta.env.VITE_DEMO_MODE at build time.
// The unused branch is dead-code-eliminated, so uploadApiMock.js
// is NEVER included in a production bundle.
//
// Consumers (UploadPage, useIngestStatus) import from here — they
// remain oblivious to which implementation is active.

import { uploadFile, fetchIngestStatus } from './uploadApi'
import { mockUploadFile, mockFetchIngestStatus } from './uploadApiMock'

const DEMO = import.meta.env.VITE_DEMO_MODE === 'true'

/**
 * Upload a file. Resolves to { source_id, status }.
 * In demo mode: simulated. In production: real POST /api/ingest/upload.
 *
 * @type {(file: File) => Promise<{ source_id: string, status: string }>}
 */
export const uploadFileFn = DEMO ? mockUploadFile : uploadFile

/**
 * Fetch ingest status for a source. Resolves to { status }.
 * In demo mode: simulated. In production: real GET /api/ingest/status/{id}.
 *
 * @type {(sourceId: string) => Promise<{ status: string }>}
 */
export const fetchIngestStatusFn = DEMO ? mockFetchIngestStatus : fetchIngestStatus
