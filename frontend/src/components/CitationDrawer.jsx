// CitationDrawer — right-side slide-over panel for citation detail.
// Opens when a citation pill or sources row is clicked.
// Closes on: × button, overlay click, Escape key.
//
// Reference: docs/API_CONTRACTS.md §Citation
//   num, source_name, modality, page, timestamp_start, timestamp_end, text

import { useEffect } from 'react'
import {
  X, FileText, Music, Image as ImageIcon,
  BookOpen, Clock,
} from 'lucide-react'
import { MODALITY_COLORS } from '../lib/constants'

// ── Helpers ────────────────────────────────────────────────────────────────

const MODALITY_ICON  = { text: FileText, audio: Music, image: ImageIcon }
const MODALITY_LABEL = {
  text:  'Text Document',
  audio: 'Audio',
  image: 'Image',
}

function formatTimestamp(seconds) {
  if (seconds === null || seconds === undefined) return '—'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

// ── Component ──────────────────────────────────────────────────────────────

/**
 * Citation slide-over drawer.
 * @param {{
 *   citation: Citation | null,
 *   onClose:  () => void,
 * }} props
 */
export default function CitationDrawer({ citation, onClose }) {
  const isOpen = citation !== null

  // ── Body scroll lock ───────────────────────────────────────────────────
  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [isOpen])

  // ── Escape key ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (!isOpen) return
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  // ── Derived values (safe-guarded for when citation is null) ────────────
  const modality   = citation?.modality ?? 'text'
  const modalColor = MODALITY_COLORS[modality] ?? MODALITY_COLORS.text
  const FileIcon   = MODALITY_ICON[modality]   ?? FileText

  const hasPage      = citation?.page !== null && citation?.page !== undefined
  const hasTimestamp = !hasPage &&
    citation?.timestamp_start !== null &&
    citation?.timestamp_start !== undefined

  return (
    /* Portal-like wrapper — fixed, always in DOM, z-50 */
    <div
      className="fixed inset-0 z-50"
      style={{ pointerEvents: isOpen ? 'auto' : 'none' }}
      role={isOpen ? 'dialog' : undefined}
      aria-modal={isOpen || undefined}
      aria-label="Citation detail"
    >
      {/* ── Dim overlay ── */}
      <div
        className="absolute inset-0 transition-opacity duration-300"
        style={{
          background: 'rgba(0,0,0,0.55)',
          opacity:    isOpen ? 1 : 0,
        }}
        onClick={onClose}
      />

      {/* ── Slide-over panel ── */}
      <div
        id="citation-drawer"
        className="absolute right-0 top-0 h-full flex flex-col transition-transform duration-300"
        style={{
          width:       420,
          maxWidth:    '90vw',
          background:  'var(--bg-surface)',
          borderLeft:  '1px solid var(--border-strong)',
          transform:   isOpen ? 'translateX(0)' : 'translateX(100%)',
          boxShadow:   isOpen ? '-8px 0 32px rgba(0,0,0,0.4)' : 'none',
        }}
      >
        {/* ── Panel header ── */}
        <div
          className="flex items-center justify-between px-5 py-4 border-b shrink-0"
          style={{ borderColor: 'var(--border)' }}
        >
          <div className="flex items-center gap-2.5">
            {citation && (
              <div
                className="flex items-center justify-center w-6 h-6 rounded text-xs font-bold shrink-0"
                style={{
                  background: 'rgba(29,158,117,0.18)',
                  color:      '#43ce9e',
                  border:     '1px solid rgba(29,158,117,0.3)',
                }}
              >
                {citation.num}
              </div>
            )}
            <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
              Citation Source
            </span>
          </div>

          <button
            id="citation-drawer-close"
            onClick={onClose}
            title="Close (Esc)"
            className="flex items-center justify-center w-7 h-7 rounded-lg transition-colors"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.08)'
              e.currentTarget.style.color      = 'var(--text-primary)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.color      = 'var(--text-muted)'
            }}
          >
            <X size={15} />
          </button>
        </div>

        {/* ── Panel body — only populated when open ── */}
        {citation && (
          <div className="flex-1 overflow-y-auto px-5 py-5 space-y-5">

            {/* File name */}
            <div>
              <p className="text-xs font-medium mb-1 uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>
                File
              </p>
              <p className="text-sm font-medium break-all" style={{ color: 'var(--text-primary)' }}>
                {citation.source_name}
              </p>
            </div>

            {/* File type + location row */}
            <div
              className="flex items-center gap-3 px-4 py-3 rounded-xl"
              style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}
            >
              {/* Modality icon */}
              <div
                className="flex items-center justify-center w-9 h-9 rounded-lg shrink-0"
                style={{ background: `${modalColor}18` }}
              >
                <FileIcon size={16} style={{ color: modalColor }} />
              </div>

              {/* Modality label */}
              <div className="flex-1 min-w-0">
                <p className="text-xs mb-1" style={{ color: 'var(--text-muted)' }}>Type</p>
                <span
                  className="text-xs px-2 py-0.5 rounded font-medium"
                  style={{ background: `${modalColor}18`, color: modalColor }}
                >
                  {MODALITY_LABEL[modality] ?? modality}
                </span>
              </div>

              {/* Page number */}
              {hasPage && (
                <div className="shrink-0 text-right">
                  <p className="text-xs mb-1" style={{ color: 'var(--text-muted)' }}>Page</p>
                  <div className="flex items-center gap-1 justify-end">
                    <BookOpen size={11} style={{ color: 'var(--text-secondary)' }} />
                    <span className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>
                      {citation.page}
                    </span>
                  </div>
                </div>
              )}

              {/* Timestamp */}
              {hasTimestamp && (
                <div className="shrink-0 text-right">
                  <p className="text-xs mb-1" style={{ color: 'var(--text-muted)' }}>Timestamp</p>
                  <div className="flex items-center gap-1 justify-end">
                    <Clock size={11} style={{ color: 'var(--text-secondary)' }} />
                    <span className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>
                      {formatTimestamp(citation.timestamp_start)}
                      {citation.timestamp_end !== null &&
                        ` – ${formatTimestamp(citation.timestamp_end)}`}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Evidence snippet */}
            <div>
              <p
                className="text-xs font-semibold mb-2 uppercase tracking-wide"
                style={{ color: 'var(--text-muted)' }}
              >
                Evidence Snippet
              </p>
              <div
                className="px-4 py-3.5 rounded-xl leading-6"
                style={{
                  background:  'var(--bg-elevated)',
                  border:      '1px solid var(--border)',
                  color:       'var(--text-secondary)',
                  fontFamily:  "'JetBrains Mono', monospace",
                  fontSize:    '0.8125rem',
                }}
              >
                &ldquo;{citation.text}&rdquo;
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  )
}
