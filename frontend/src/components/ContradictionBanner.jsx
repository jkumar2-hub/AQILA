// ContradictionBanner — amber warning shown when contradiction_found === true.
// Displays both conflicting claims and the conflict type/confidence.
//
// Reference: docs/API_CONTRACTS.md §Contradiction
//   conflict_type: 'date' | 'name' | 'location' | 'fact'

import { AlertTriangle } from 'lucide-react'

const CONFLICT_LABEL = {
  date:     'Date conflict',
  name:     'Name conflict',
  location: 'Location conflict',
  fact:     'Fact conflict',
}

/**
 * @param {{ detail: Contradiction }} props
 * detail = { claim_a, claim_b, source_a, source_b, conflict_type, confidence }
 */
export default function ContradictionBanner({ detail }) {
  if (!detail) return null

  const label      = CONFLICT_LABEL[detail.conflict_type] ?? detail.conflict_type
  const confidence = Math.round(detail.confidence * 100)

  return (
    <div
      id="contradiction-banner"
      className="rounded-xl p-4"
      style={{
        background: 'rgba(239,159,39,0.08)',
        border:     '1px solid rgba(239,159,39,0.28)',
      }}
    >
      {/* Header row */}
      <div className="flex items-center gap-2 mb-3 flex-wrap">
        <AlertTriangle size={14} style={{ color: 'var(--accent-amber)' }} />
        <span className="text-sm font-semibold" style={{ color: 'var(--accent-amber)' }}>
          Contradiction Detected
        </span>

        {/* Conflict type pill */}
        <span
          className="px-2 py-0.5 rounded-full text-xs font-medium"
          style={{
            background: 'rgba(239,159,39,0.18)',
            color:      'var(--accent-amber)',
          }}
        >
          {label}
        </span>

        {/* Confidence */}
        <span
          className="ml-auto text-xs font-mono"
          style={{ color: 'rgba(239,159,39,0.65)' }}
        >
          {confidence}% confidence
        </span>
      </div>

      {/* Claims grid */}
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {[
          { label: 'Claim A', text: detail.claim_a },
          { label: 'Claim B', text: detail.claim_b },
        ].map(({ label: claimLabel, text }) => (
          <div
            key={claimLabel}
            className="rounded-lg px-3 py-2.5"
            style={{
              background: 'rgba(239,159,39,0.05)',
              border:     '1px solid rgba(239,159,39,0.14)',
            }}
          >
            <p
              className="text-xs font-semibold mb-1 uppercase tracking-wide"
              style={{ color: 'rgba(239,159,39,0.55)' }}
            >
              {claimLabel}
            </p>
            <p className="text-xs leading-5" style={{ color: 'var(--text-secondary)' }}>
              {text}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
