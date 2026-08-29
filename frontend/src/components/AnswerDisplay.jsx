// AnswerDisplay — renders AQILAResponse.answer with [N] citation pills.
// [N] markers in the answer string are replaced with teal pill buttons.
// Clicking a pill calls onCitationClick(num).
//
// Reference: docs/API_CONTRACTS.md §Citation (num matches [N] in answer)

/**
 * @param {{
 *   answer:           string,
 *   citations:        Citation[],
 *   onCitationClick:  (num: number) => void,
 * }} props
 */
export default function AnswerDisplay({ answer, citations, onCitationClick }) {
  // Split on [N] markers, keeping delimiters in the array
  // e.g. "...confirmed [1]. A report..." → ["...confirmed ", "[1]", ". A report..."]
  const parts = answer.split(/(\[\d+\])/g)

  return (
    <div className="text-sm leading-7" style={{ color: 'var(--text-primary)' }}>
      {parts.map((part, i) => {
        const match = part.match(/^\[(\d+)\]$/)
        if (!match) {
          return <span key={i}>{part}</span>
        }

        const num = parseInt(match[1], 10)
        const citation = citations.find((c) => c.num === num)

        return (
          <button
            key={i}
            id={`citation-pill-${num}`}
            onClick={() => onCitationClick(num)}
            title={citation ? `${citation.source_name} — click to view` : `Citation ${num}`}
            className="inline-flex items-center justify-center mx-0.5 align-middle cursor-pointer transition-all duration-100"
            style={{
              padding:      '1px 6px',
              borderRadius: 5,
              background:   'rgba(29,158,117,0.18)',
              color:        '#43ce9e',
              border:       '1px solid rgba(29,158,117,0.35)',
              fontSize:     '0.75rem',
              fontWeight:   600,
              lineHeight:   1.6,
              verticalAlign: 'middle',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(29,158,117,0.32)'
              e.currentTarget.style.transform  = 'scale(1.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(29,158,117,0.18)'
              e.currentTarget.style.transform  = 'scale(1)'
            }}
          >
            {num}
          </button>
        )
      })}
    </div>
  )
}
