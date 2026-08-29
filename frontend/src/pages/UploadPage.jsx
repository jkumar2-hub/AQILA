import { useState, useCallback } from 'react'
import { Upload, FolderOpen, FlaskConical } from 'lucide-react'
import UploadDropzone from '../components/UploadDropzone'
import UploadCard from '../components/UploadCard'
import { uploadFileFn } from '../lib/uploadService'

// True only when VITE_DEMO_MODE=true is set in .env.development.local
// Vite eliminates this branch in production builds.
const DEMO = import.meta.env.VITE_DEMO_MODE === 'true'

// ── Helpers ────────────────────────────────────────────────────────────────

/** Create a fresh file entry in 'ready' state */
function createEntry(file) {
  return {
    id:       crypto.randomUUID(),
    file,
    status:   'ready',   // 'ready' | 'uploading' | 'processing' | 'indexed' | 'failed'
    sourceId: null,
    error:    null,
  }
}

// ── Page ───────────────────────────────────────────────────────────────────

/**
 * UploadPage — M3 P0
 *
 * State shape: fileEntries[]
 *   { id, file, status, sourceId, error }
 *
 * Upload lifecycle:
 *   handleAccept → addEntries → startUpload (per file)
 *     uploading → POST /api/ingest/upload → processing (sourceId stored)
 *     UploadCard polls GET /api/ingest/status/{id} → onStatusChange
 *     onStatusChange → updates status to 'indexed' | 'failed'
 */
export default function UploadPage() {
  const [fileEntries, setFileEntries] = useState([])

  // ── Upload a single entry ──────────────────────────────────────────────
  const startUpload = useCallback(async (id, file) => {
    // Mark as uploading
    setFileEntries(prev =>
      prev.map(e => e.id === id ? { ...e, status: 'uploading', error: null } : e)
    )

    try {
      const { source_id } = await uploadFileFn(file)

      // Upload succeeded — hand off to polling
      setFileEntries(prev =>
        prev.map(e =>
          e.id === id
            ? { ...e, status: 'processing', sourceId: source_id }
            : e
        )
      )
    } catch (err) {
      setFileEntries(prev =>
        prev.map(e =>
          e.id === id
            ? { ...e, status: 'failed', error: err.message }
            : e
        )
      )
    }
  }, [])

  // ── Dropzone accepted files ────────────────────────────────────────────
  const handleAccept = useCallback((files) => {
    const newEntries = files.map(createEntry)
    setFileEntries(prev => [...prev, ...newEntries])
    // Start uploading each file immediately
    newEntries.forEach(entry => startUpload(entry.id, entry.file))
  }, [startUpload])

  // ── Remove a file (ready or failed only) ──────────────────────────────
  const handleRemove = useCallback((id) => {
    setFileEntries(prev => prev.filter(e => e.id !== id))
  }, [])

  // ── Retry a failed upload ──────────────────────────────────────────────
  const handleRetry = useCallback((id) => {
    // Read the file from current state, then re-trigger upload
    setFileEntries(prev => {
      const entry = prev.find(e => e.id === id)
      if (entry) {
        // Reset to ready before uploading (upload sets to 'uploading' next tick)
        setTimeout(() => startUpload(id, entry.file), 0)
        return prev.map(e =>
          e.id === id ? { ...e, status: 'ready', error: null, sourceId: null } : e
        )
      }
      return prev
    })
  }, [startUpload])

  // ── Status change from UploadCard's polling hook ───────────────────────
  const handleStatusChange = useCallback((id, newStatus) => {
    setFileEntries(prev =>
      prev.map(e => e.id === id ? { ...e, status: newStatus } : e)
    )
  }, [])

  // ── Derived counts for the summary bar ────────────────────────────────
  const total     = fileEntries.length
  const indexed   = fileEntries.filter(e => e.status === 'indexed').length
  const active    = fileEntries.filter(e => e.status === 'uploading' || e.status === 'processing').length
  const failed    = fileEntries.filter(e => e.status === 'failed').length

  return (
    <div className="flex flex-col min-h-full px-8 py-8" style={{ maxWidth: 860 }}>

      {/* ── Demo mode banner ── */}
      {DEMO && (
        <div
          className="flex items-center gap-2.5 px-4 py-2.5 mb-6 rounded-lg text-xs font-medium"
          style={{
            background: 'rgba(239,159,39,0.10)',
            border:     '1px solid rgba(239,159,39,0.28)',
            color:      'var(--accent-amber)',
          }}
        >
          <FlaskConical size={14} strokeWidth={2} />
          <span>
            <strong>DEMO MODE</strong> — API calls are simulated. No backend required.
            Every 4th file will show a Failed state to demonstrate Retry.
          </span>
        </div>
      )}

      {/* ── Page header ── */}
      <div className="mb-7">
        <div className="flex items-center gap-3 mb-2">
          <div
            className="flex items-center justify-center w-9 h-9 rounded-lg"
            style={{
              background: 'rgba(29,158,117,0.15)',
              border:     '1px solid rgba(29,158,117,0.3)',
            }}
          >
            <Upload size={18} style={{ color: 'var(--accent-teal)' }} />
          </div>
          <h1 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
            Upload Documents
          </h1>
        </div>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Ingest intelligence documents into the AQILA knowledge base.
          Each file is processed and indexed automatically.
        </p>
      </div>

      {/* ── Drop zone ── */}
      <UploadDropzone onAccept={handleAccept} />

      {/* ── Summary bar (only when files exist) ── */}
      {total > 0 && (
        <div
          className="flex items-center gap-4 mt-5 px-4 py-2.5 rounded-lg text-xs"
          style={{
            background:  'var(--bg-elevated)',
            border:      '1px solid var(--border)',
            color:       'var(--text-muted)',
          }}
        >
          <span>{total} file{total !== 1 ? 's' : ''}</span>
          {indexed > 0 && (
            <span style={{ color: 'var(--accent-teal)' }}>
              ✓ {indexed} indexed
            </span>
          )}
          {active > 0 && (
            <span style={{ color: 'var(--accent-amber)' }}>
              ⟳ {active} in progress
            </span>
          )}
          {failed > 0 && (
            <span style={{ color: '#f87171' }}>
              ✗ {failed} failed
            </span>
          )}

          {/* Clear completed */}
          {indexed > 0 && (
            <button
              className="ml-auto text-xs transition-colors"
              style={{ color: 'var(--text-muted)' }}
              onMouseEnter={e => e.currentTarget.style.color = 'var(--text-secondary)'}
              onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
              onClick={() =>
                setFileEntries(prev => prev.filter(e => e.status !== 'indexed'))
              }
            >
              Clear indexed
            </button>
          )}
        </div>
      )}

      {/* ── File cards ── */}
      {total > 0 && (
        <div className="mt-4 flex flex-col gap-2.5">
          {fileEntries.map(entry => (
            <UploadCard
              key={entry.id}
              entry={entry}
              onRemove={handleRemove}
              onRetry={handleRetry}
              onStatusChange={handleStatusChange}
            />
          ))}
        </div>
      )}

      {/* ── Empty state helper text ── */}
      {total === 0 && (
        <div className="mt-6 flex items-center gap-2 text-xs" style={{ color: 'var(--text-muted)' }}>
          <FolderOpen size={14} />
          <span>No files added yet. Drop files above or click to browse.</span>
        </div>
      )}
    </div>
  )
}
