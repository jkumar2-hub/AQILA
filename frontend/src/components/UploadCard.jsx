import { useEffect } from 'react'
import {
  FileText, Music, Image, X, RefreshCw,
  CheckCircle2, XCircle, Loader2, Clock,
} from 'lucide-react'
import { useIngestStatus } from '../hooks/useIngestStatus'
import { MODALITY_COLORS } from '../lib/constants'
import { cn } from '../lib/cn'

// ── Helpers ────────────────────────────────────────────────────────────────

/** Map MIME type → AQILA modality string */
function getModality(file) {
  const t = file.type
  if (t === 'application/pdf' || t.includes('wordprocessingml')) return 'text'
  if (t.startsWith('audio/')) return 'audio'
  if (t.startsWith('image/')) return 'image'
  return 'text'
}

/** Modality → display label */
const MODALITY_LABEL = { text: 'Text', audio: 'Audio', image: 'Image' }

/** Modality → Lucide icon component */
const MODALITY_ICON = { text: FileText, audio: Music, image: Image }

/** Format bytes to human-readable size */
function formatBytes(bytes) {
  if (bytes === 0) return '0 B'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// ── Status badge ───────────────────────────────────────────────────────────

const STATUS_CONFIG = {
  ready: {
    label: 'Ready',
    color: 'var(--text-muted)',
    bg:    'rgba(72,79,88,0.20)',
    Icon:  Clock,
    spin:  false,
    pulse: false,
  },
  uploading: {
    label: 'Uploading…',
    color: '#60a5fa',
    bg:    'rgba(96,165,250,0.12)',
    Icon:  Loader2,
    spin:  true,
    pulse: false,
  },
  processing: {
    label: 'Processing…',
    color: 'var(--accent-amber)',
    bg:    'rgba(239,159,39,0.12)',
    Icon:  Loader2,
    spin:  true,
    pulse: false,
  },
  indexed: {
    label: 'Indexed ✓',
    color: 'var(--accent-teal)',
    bg:    'rgba(29,158,117,0.15)',
    Icon:  CheckCircle2,
    spin:  false,
    pulse: false,
  },
  failed: {
    label: 'Failed',
    color: '#f87171',
    bg:    'rgba(248,113,113,0.12)',
    Icon:  XCircle,
    spin:  false,
    pulse: false,
  },
}

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.ready
  const { Icon } = cfg
  return (
    <div
      className="flex items-center gap-1.5 px-2.5 py-1 rounded-full shrink-0"
      style={{ background: cfg.bg }}
    >
      <Icon
        size={13}
        strokeWidth={2}
        style={{ color: cfg.color }}
        className={cn(cfg.spin && 'animate-spin')}
      />
      <span className="text-xs font-medium whitespace-nowrap" style={{ color: cfg.color }}>
        {cfg.label}
      </span>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────────────────────

/**
 * UploadCard — per-file card with live status.
 *
 * Polling lifecycle:
 *   When entry.status === 'processing' and entry.sourceId is set,
 *   this component polls GET /api/ingest/status/{sourceId} every 1s
 *   and calls onStatusChange(entry.id, newStatus) when it reaches
 *   'indexed' or 'failed'.
 *
 * @param {{
 *   entry:          { id: string, file: File, status: string, sourceId: string|null, error: string|null },
 *   onRemove:       (id: string) => void,
 *   onRetry:        (id: string) => void,
 *   onStatusChange: (id: string, status: string) => void,
 * }} props
 */
export default function UploadCard({ entry, onRemove, onRetry, onStatusChange }) {
  const modality    = getModality(entry.file)
  const modalColor  = MODALITY_COLORS[modality]
  const FileIcon    = MODALITY_ICON[modality]

  // ── Polling ──────────────────────────────────────────────────────────────
  const isPolling = entry.status === 'processing'
  const { data: statusData, isError: statusError } = useIngestStatus(
    entry.sourceId,
    isPolling,
  )

  // Propagate terminal status back to the page
  useEffect(() => {
    if (!statusData?.status) return
    const { status } = statusData
    if (status === 'indexed' || status === 'failed') {
      onStatusChange(entry.id, status)
    }
  }, [statusData?.status, entry.id, onStatusChange])

  // Network error during polling → mark as failed
  useEffect(() => {
    if (statusError && entry.status === 'processing') {
      onStatusChange(entry.id, 'failed')
    }
  }, [statusError, entry.status, entry.id, onStatusChange])

  // ── Actions visibility ────────────────────────────────────────────────────
  const canRemove = entry.status === 'ready' || entry.status === 'failed'
  const canRetry  = entry.status === 'failed'
  const isActive  = entry.status === 'uploading' || entry.status === 'processing'

  return (
    <div
      className={cn(
        'flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200',
        isActive && 'animate-pulse-subtle',
      )}
      style={{
        background: 'var(--bg-elevated)',
        border: `1px solid ${entry.status === 'indexed'
          ? 'rgba(29,158,117,0.3)'
          : entry.status === 'failed'
          ? 'rgba(248,113,113,0.25)'
          : 'var(--border)'}`,
      }}
    >
      {/* Modality colour bar */}
      <div
        className="w-0.5 self-stretch rounded-full shrink-0"
        style={{ background: modalColor, opacity: 0.7 }}
      />

      {/* File type icon */}
      <div
        className="flex items-center justify-center w-8 h-8 rounded-lg shrink-0"
        style={{ background: `${modalColor}18` }}
      >
        <FileIcon size={15} style={{ color: modalColor }} />
      </div>

      {/* File metadata */}
      <div className="flex-1 min-w-0">
        <p
          className="text-sm font-medium truncate"
          title={entry.file.name}
          style={{ color: 'var(--text-primary)' }}
        >
          {entry.file.name}
        </p>
        <div className="flex items-center gap-1.5 mt-0.5 flex-wrap">
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
            {formatBytes(entry.file.size)}
          </span>
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>·</span>
          {/* Modality badge */}
          <span
            className="text-xs px-1.5 py-0.5 rounded font-medium"
            style={{ background: `${modalColor}18`, color: modalColor }}
          >
            {MODALITY_LABEL[modality]}
          </span>
        </div>
        {/* Error message */}
        {entry.status === 'failed' && entry.error && (
          <p className="text-xs mt-1 truncate" style={{ color: '#fca5a5' }} title={entry.error}>
            {entry.error}
          </p>
        )}
      </div>

      {/* Status badge */}
      <StatusBadge status={entry.status} />

      {/* Retry button */}
      {canRetry && (
        <button
          onClick={() => onRetry(entry.id)}
          title="Retry upload"
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors shrink-0"
          style={{
            background: 'rgba(29,158,117,0.12)',
            color: '#43ce9e',
            border: '1px solid rgba(29,158,117,0.25)',
          }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(29,158,117,0.22)'}
          onMouseLeave={e => e.currentTarget.style.background = 'rgba(29,158,117,0.12)'}
        >
          <RefreshCw size={11} />
          Retry
        </button>
      )}

      {/* Remove button */}
      {canRemove && (
        <button
          onClick={() => onRemove(entry.id)}
          title="Remove file"
          className="flex items-center justify-center w-6 h-6 rounded-md transition-colors shrink-0"
          style={{ color: 'var(--text-muted)' }}
          onMouseEnter={e => {
            e.currentTarget.style.background = 'rgba(248,113,113,0.12)'
            e.currentTarget.style.color = '#f87171'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = 'transparent'
            e.currentTarget.style.color = 'var(--text-muted)'
          }}
        >
          <X size={13} />
        </button>
      )}
    </div>
  )
}
