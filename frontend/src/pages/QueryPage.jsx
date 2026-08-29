// QueryPage — M3 P0 implementation
// Uses queryService.js (mock today, real API when M4 integrates).
//
// State machine:
//   empty   → isLoading + result null + error null    (initial)
//   loading → isLoading true
//   error   → error string set
//   result  → result (AQILAResponse) set
//   drawer  → activeCitation set (overlays result)

import { useState, useCallback, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search, Zap, Loader2, AlertCircle, GitFork, Clock, RotateCcw,
} from 'lucide-react'
import { cn } from '../lib/cn'
import { runQuery } from '../lib/queryService'
import AnswerDisplay       from '../components/AnswerDisplay'
import ContradictionBanner from '../components/ContradictionBanner'
import CitationDrawer      from '../components/CitationDrawer'

// ── Component ──────────────────────────────────────────────────────────────

export default function QueryPage() {
  const navigate     = useNavigate()
  const textareaRef  = useRef(null)

  const [queryText,      setQueryText]      = useState('')
  const [isLoading,      setIsLoading]      = useState(false)
  const [result,         setResult]         = useState(null)   // AQILAResponse | null
  const [error,          setError]          = useState(null)   // string | null
  const [activeCitation, setActiveCitation] = useState(null)  // Citation | null

  // ── Auto-resize textarea ──────────────────────────────────────────────
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = `${Math.min(ta.scrollHeight, 240)}px`
  }, [queryText])

  // ── Submit handler ────────────────────────────────────────────────────
  const handleSubmit = useCallback(async () => {
    if (!queryText.trim() || isLoading) return
    setIsLoading(true)
    setError(null)
    setResult(null)
    setActiveCitation(null)
    try {
      const data = await runQuery(queryText)
      setResult(data)
    } catch (e) {
      setError(e?.message || 'Query failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [queryText, isLoading])

  // Ctrl+Enter or Cmd+Enter to submit
  function handleKeyDown(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      handleSubmit()
    }
  }

  // ── Citation click ────────────────────────────────────────────────────
  const handleCitationClick = useCallback((num) => {
    if (!result) return
    const found = result.citations.find((c) => c.num === num)
    if (found) setActiveCitation(found)
  }, [result])

  const canSubmit = queryText.trim().length > 0 && !isLoading

  // ── Render ────────────────────────────────────────────────────────────
  return (
    <>
      {/* Main scroll area */}
      <div className="flex flex-col min-h-full px-8 py-8" style={{ maxWidth: 860 }}>

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
              <Search size={18} style={{ color: 'var(--accent-teal)' }} />
            </div>
            <h1 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
              Query
            </h1>
          </div>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Ask a natural-language question. AQILA retrieves evidence, detects contradictions, and cites sources.
          </p>
        </div>

        {/* ── Query input card ── */}
        <div
          className="rounded-xl p-4 mb-6"
          style={{
            background: 'var(--bg-elevated)',
            border:     '1px solid var(--border)',
          }}
        >
          <textarea
            id="aqila-query-input"
            ref={textareaRef}
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about your documents…"
            style={{
              width:       '100%',
              minHeight:   80,
              maxHeight:   240,
              resize:      'none',
              overflowY:   'auto',
              background:  'var(--bg-overlay)',
              border:      '1px solid var(--border-strong)',
              borderRadius: 8,
              padding:     '10px 14px',
              fontSize:    '0.875rem',
              color:       'var(--text-primary)',
              outline:     'none',
              fontFamily:  'Inter, system-ui, sans-serif',
              lineHeight:  1.65,
              transition:  'border-color 0.15s',
            }}
            onFocus={(e)  => (e.currentTarget.style.borderColor = 'rgba(29,158,117,0.55)')}
            onBlur={(e)   => (e.currentTarget.style.borderColor = 'var(--border-strong)')}
          />

          <div className="flex items-center justify-between mt-3">
            <p className="text-xs select-none" style={{ color: 'var(--text-muted)' }}>
              {navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'}+Enter to submit
            </p>

            <button
              id="aqila-run-query-btn"
              onClick={handleSubmit}
              disabled={!canSubmit}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-150',
                !canSubmit ? 'opacity-40 cursor-not-allowed' : 'hover:brightness-110',
              )}
              style={{ background: 'var(--accent-teal)', color: '#fff' }}
            >
              {isLoading
                ? <Loader2 size={14} className="animate-spin" />
                : <Zap      size={14} />
              }
              {isLoading ? 'Analysing…' : 'Run Query'}
            </button>
          </div>
        </div>

        {/* ── Loading state ── */}
        {isLoading && (
          <div
            className="flex flex-col items-center justify-center gap-3 py-16 rounded-xl"
            style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}
          >
            <Loader2
              size={30}
              className="animate-spin"
              style={{ color: 'var(--accent-teal)' }}
            />
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Analysing documents…
            </p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              Retrieving evidence · Detecting contradictions · Citing sources
            </p>
          </div>
        )}

        {/* ── Error state ── */}
        {!isLoading && error && (
          <div
            className="flex items-start gap-3 px-4 py-4 rounded-xl"
            style={{
              background: 'rgba(248,113,113,0.08)',
              border:     '1px solid rgba(248,113,113,0.25)',
            }}
          >
            <AlertCircle
              size={16}
              className="shrink-0 mt-0.5"
              style={{ color: '#f87171' }}
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium mb-0.5" style={{ color: '#f87171' }}>
                Query failed
              </p>
              <p className="text-xs" style={{ color: '#fca5a5' }}>
                {error}
              </p>
            </div>
            <button
              onClick={handleSubmit}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium shrink-0 transition-colors"
              style={{
                background: 'rgba(248,113,113,0.12)',
                color:      '#f87171',
                border:     '1px solid rgba(248,113,113,0.25)',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(248,113,113,0.22)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(248,113,113,0.12)')}
            >
              <RotateCcw size={11} />
              Retry
            </button>
          </div>
        )}

        {/* ── Empty state ── */}
        {!isLoading && !error && !result && (
          <div
            className="flex flex-col items-center justify-center gap-3 py-16 rounded-xl"
            style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}
          >
            <Search
              size={30}
              className="opacity-20"
              style={{ color: 'var(--text-secondary)' }}
            />
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              Enter a question above to query the knowledge base.
            </p>
          </div>
        )}

        {/* ── Result region ── */}
        {!isLoading && result && (
          <div className="flex flex-col gap-4">

            {/* Contradiction banner */}
            {result.contradiction_found && result.contradiction_detail && (
              <ContradictionBanner detail={result.contradiction_detail} />
            )}

            {/* Answer card */}
            <div
              className="px-6 py-5 rounded-xl"
              style={{
                background: 'var(--bg-elevated)',
                border:     '1px solid var(--border)',
              }}
            >
              {/* Section label */}
              <div className="flex items-center gap-2 mb-4">
                <div
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ background: 'var(--accent-teal)' }}
                />
                <span
                  className="text-xs font-semibold uppercase tracking-wider"
                  style={{ color: 'var(--text-muted)' }}
                >
                  Answer
                </span>
              </div>

              {/* Answer text with citation pills */}
              <AnswerDisplay
                answer={result.answer}
                citations={result.citations}
                onCitationClick={handleCitationClick}
              />

              {/* Sources list */}
              {result.citations.length > 0 && (
                <div
                  className="mt-5 pt-4 border-t"
                  style={{ borderColor: 'var(--border)' }}
                >
                  <p
                    className="text-xs font-semibold uppercase tracking-wider mb-2"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    Sources
                  </p>
                  <div className="flex flex-col gap-1">
                    {result.citations.map((c) => (
                      <button
                        key={c.num}
                        id={`source-row-${c.num}`}
                        onClick={() => setActiveCitation(c)}
                        className="flex items-center gap-2.5 text-left rounded-lg px-2 py-1.5 w-full transition-colors"
                        style={{ color: 'var(--text-secondary)' }}
                        onMouseEnter={(e) =>
                          (e.currentTarget.style.background = 'rgba(255,255,255,0.04)')
                        }
                        onMouseLeave={(e) =>
                          (e.currentTarget.style.background = 'transparent')
                        }
                      >
                        <span
                          className="flex items-center justify-center w-5 h-5 rounded text-xs font-bold shrink-0"
                          style={{
                            background: 'rgba(29,158,117,0.18)',
                            color:      '#43ce9e',
                          }}
                        >
                          {c.num}
                        </span>
                        <span className="text-xs flex-1 truncate">
                          {c.source_name}
                        </span>
                        {c.page !== null && c.page !== undefined && (
                          <span
                            className="text-xs ml-auto shrink-0"
                            style={{ color: 'var(--text-muted)' }}
                          >
                            p.&nbsp;{c.page}
                          </span>
                        )}
                        {c.timestamp_start !== null &&
                          c.timestamp_start !== undefined && (
                          <span
                            className="text-xs ml-auto shrink-0"
                            style={{ color: 'var(--text-muted)' }}
                          >
                            {Math.floor(c.timestamp_start / 60)}:
                            {String(Math.floor(c.timestamp_start % 60)).padStart(2, '0')}
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Footer row: response time + View Evidence */}
            <div className="flex items-center justify-between pb-2">
              <span
                className="flex items-center gap-1.5 text-xs"
                style={{ color: 'var(--text-muted)' }}
              >
                <Clock size={12} />
                {result.response_time_ms.toLocaleString()} ms
              </span>

              <button
                id="view-evidence-btn"
                onClick={() => navigate('/evidence')}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150"
                style={{
                  background: 'rgba(83,74,183,0.14)',
                  border:     '1px solid rgba(83,74,183,0.3)',
                  color:      '#9b93ed',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(83,74,183,0.24)'
                  e.currentTarget.style.color      = '#b3aef2'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(83,74,183,0.14)'
                  e.currentTarget.style.color      = '#9b93ed'
                }}
              >
                <GitFork size={14} />
                View Evidence
              </button>
            </div>

          </div>
        )}
      </div>

      {/* Citation drawer — fixed overlay, rendered outside main flow */}
      <CitationDrawer
        citation={activeCitation}
        onClose={() => setActiveCitation(null)}
      />
    </>
  )
}
