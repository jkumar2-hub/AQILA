// EvidencePage — M3 P0 implementation
// Renders AQILAResponse.evidence as a force-directed graph using react-force-graph-2d.
//
// Data flow:
//   evidenceService.fetchEvidenceGraph() → { nodes, edges }
//   → ForceGraph2D (react-force-graph-2d)
//   → click node → NodeDetailPanel (right-side slide-over)
//
// Node colours come from node.color (supplied by backend/mock, not re-derived here).
// Edge styles vary by edge_type: semantic | temporal | both.
//
// M4 integration: replace evidenceService body — this file needs no changes.
// Reference: docs/API_CONTRACTS.md §EvidenceGraph

import { useState, useEffect, useRef, useCallback } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import {
  GitFork, X, FileText, Music, Image as ImageIcon,
  Loader2, AlertCircle, ZoomIn, ZoomOut, Maximize2,
} from 'lucide-react'
import { fetchEvidenceGraph } from '../lib/evidenceService'
import { MODALITY_COLORS } from '../lib/constants'

// ── Constants ──────────────────────────────────────────────────────────────

const EDGE_STYLE = {
  semantic: { color: 'rgba(29,158,117,0.55)',  dash: null,   width: 1.5 },
  temporal: { color: 'rgba(239,159,39,0.55)',  dash: [4, 3], width: 1.5 },
  both:     { color: 'rgba(255,255,255,0.45)', dash: null,   width: 2   },
}

const MODALITY_ICON  = { text: FileText, audio: Music, image: ImageIcon }
const MODALITY_LABEL = { text: 'Text Document', audio: 'Audio', image: 'Image' }

// ── Helpers ────────────────────────────────────────────────────────────────

/** Convert EvidenceGraph edges to react-force-graph-2d link format */
function buildGraphData(nodes, edges) {
  return {
    nodes: nodes.map((n) => ({ ...n })),  // shallow copy keeps id/label/color/etc.
    links: edges.map((e) => ({
      source:       e.source,
      target:       e.target,
      edge_type:    e.edge_type,
      similarity:   e.similarity,
      temporal_gap: e.temporal_gap,
    })),
  }
}

// ── Node detail panel ──────────────────────────────────────────────────────

function NodeDetailPanel({ node, onClose }) {
  const isOpen = node !== null

  // Escape key close
  useEffect(() => {
    if (!isOpen) return
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  const modality   = node?.modality ?? 'text'
  const modalColor = node?.color ?? MODALITY_COLORS[modality] ?? MODALITY_COLORS.text
  const NodeIcon   = MODALITY_ICON[modality] ?? FileText
  const confidence = node ? Math.round(node.confidence * 100) : 0

  return (
    <div
      className="absolute right-0 top-0 h-full flex flex-col transition-transform duration-300 z-20"
      style={{
        width:      340,
        maxWidth:   '80%',
        background: 'var(--bg-surface)',
        borderLeft: '1px solid var(--border-strong)',
        transform:  isOpen ? 'translateX(0)' : 'translateX(100%)',
        boxShadow:  isOpen ? '-8px 0 32px rgba(0,0,0,0.45)' : 'none',
      }}
    >
      {/* Panel header */}
      <div
        className="flex items-center justify-between px-5 py-4 border-b shrink-0"
        style={{ borderColor: 'var(--border)' }}
      >
        <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
          Node Detail
        </span>
        <button
          onClick={onClose}
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

      {node && (
        <div className="flex-1 overflow-y-auto px-5 py-5 space-y-5">

          {/* File icon + name */}
          <div className="flex items-center gap-3">
            <div
              className="flex items-center justify-center w-10 h-10 rounded-xl shrink-0"
              style={{ background: `${modalColor}20`, border: `1px solid ${modalColor}30` }}
            >
              <NodeIcon size={18} style={{ color: modalColor }} />
            </div>
            <div className="min-w-0">
              <p
                className="text-sm font-semibold break-all"
                style={{ color: 'var(--text-primary)' }}
              >
                {node.label}
              </p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                {node.id}
              </p>
            </div>
          </div>

          {/* Modality + confidence row */}
          <div
            className="flex items-center gap-3 px-4 py-3 rounded-xl"
            style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}
          >
            {/* Modality badge */}
            <div className="flex-1">
              <p className="text-xs mb-1" style={{ color: 'var(--text-muted)' }}>Type</p>
              <span
                className="text-xs px-2 py-0.5 rounded font-medium"
                style={{ background: `${modalColor}18`, color: modalColor }}
              >
                {MODALITY_LABEL[modality] ?? modality}
              </span>
            </div>

            {/* Confidence */}
            <div className="text-right">
              <p className="text-xs mb-1" style={{ color: 'var(--text-muted)' }}>Confidence</p>
              <p className="text-sm font-bold" style={{ color: modalColor }}>
                {confidence}%
              </p>
            </div>
          </div>

          {/* Confidence bar */}
          <div>
            <div
              className="w-full rounded-full overflow-hidden"
              style={{ height: 6, background: 'var(--bg-overlay)' }}
            >
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{ width: `${confidence}%`, background: modalColor }}
              />
            </div>
            <p className="text-xs mt-1.5" style={{ color: 'var(--text-muted)' }}>
              Relevance confidence score
            </p>
          </div>

        </div>
      )}
    </div>
  )
}

// ── Graph legend ───────────────────────────────────────────────────────────

function GraphLegend() {
  return (
    <div
      className="absolute bottom-4 left-4 flex flex-col gap-2 px-3 py-2.5 rounded-xl text-xs z-10"
      style={{
        background:  'rgba(13,17,23,0.85)',
        border:      '1px solid var(--border)',
        backdropFilter: 'blur(8px)',
      }}
    >
      <p className="font-semibold uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>
        Legend
      </p>
      {/* Edge types */}
      {[
        { label: 'Semantic', color: 'rgba(29,158,117,0.8)',   dash: false },
        { label: 'Temporal', color: 'rgba(239,159,39,0.8)',   dash: true  },
        { label: 'Both',     color: 'rgba(255,255,255,0.7)',  dash: false },
      ].map(({ label, color, dash }) => (
        <div key={label} className="flex items-center gap-2">
          <svg width="24" height="8">
            <line
              x1="0" y1="4" x2="24" y2="4"
              stroke={color}
              strokeWidth="2"
              strokeDasharray={dash ? '4 2' : undefined}
            />
          </svg>
          <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
        </div>
      ))}
    </div>
  )
}

// ── Main page ──────────────────────────────────────────────────────────────

export default function EvidencePage() {
  const containerRef = useRef(null)
  const graphRef     = useRef(null)

  const [graphData,    setGraphData]    = useState(null)  // { nodes, links } | null
  const [isLoading,    setIsLoading]    = useState(true)
  const [error,        setError]        = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [dimensions,   setDimensions]   = useState({ w: 800, h: 600 })

  // ── Load evidence data ─────────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    setError(null)

    fetchEvidenceGraph()
      .then(({ nodes, edges }) => {
        if (cancelled) return
        if (!nodes?.length) {
          setGraphData({ nodes: [], links: [] })
        } else {
          setGraphData(buildGraphData(nodes, edges ?? []))
        }
      })
      .catch((e) => {
        if (!cancelled) setError(e?.message || 'Failed to load evidence graph.')
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => { cancelled = true }
  }, [])

  // ── Measure container for ForceGraph2D width/height ───────────────────
  useEffect(() => {
    if (!containerRef.current) return
    const obs = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect
        setDimensions({ w: Math.floor(width), h: Math.floor(height) })
      }
    })
    obs.observe(containerRef.current)
    return () => obs.disconnect()
  }, [])

  // ── Custom node renderer ───────────────────────────────────────────────
  const paintNode = useCallback((node, ctx, globalScale) => {
    const isSelected = selectedNode?.id === node.id
    const radius     = isSelected ? 10 : 8
    const color      = node.color ?? MODALITY_COLORS.text

    // Glow ring for selected
    if (isSelected) {
      ctx.beginPath()
      ctx.arc(node.x, node.y, radius + 4, 0, 2 * Math.PI)
      ctx.fillStyle = `${color}30`
      ctx.fill()
    }

    // Node circle
    ctx.beginPath()
    ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI)
    ctx.fillStyle = color
    ctx.fill()

    // Border
    ctx.beginPath()
    ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI)
    ctx.strokeStyle = isSelected ? '#fff' : `${color}80`
    ctx.lineWidth   = isSelected ? 2 : 1
    ctx.stroke()

    // Label — always rendered, constant screen-space size regardless of zoom.
    // fontSize is in graph-space units: 12px screen / globalScale → always ~12px on screen.
    const SCREEN_FONT_PX = 12
    const fontSize = SCREEN_FONT_PX / globalScale
    ctx.font         = `${fontSize}px Inter, system-ui, sans-serif`
    ctx.textAlign    = 'center'
    ctx.textBaseline = 'top'
    ctx.fillStyle    = isSelected ? '#fff' : 'rgba(230,237,243,0.85)'

    // Truncate long labels
    const maxChars = 22
    const label    = node.label.length > maxChars
      ? `${node.label.slice(0, maxChars)}…`
      : node.label

    ctx.fillText(label, node.x, node.y + radius + (3 / globalScale))
  }, [selectedNode])

  // ── Custom link renderer ───────────────────────────────────────────────
  const paintLink = useCallback((link, ctx) => {
    const style = EDGE_STYLE[link.edge_type] ?? EDGE_STYLE.semantic

    ctx.strokeStyle = style.color
    ctx.lineWidth   = style.width

    if (style.dash) {
      ctx.setLineDash(style.dash)
    } else {
      ctx.setLineDash([])
    }

    // Draw the line
    ctx.beginPath()
    ctx.moveTo(link.source.x, link.source.y)
    ctx.lineTo(link.target.x, link.target.y)
    ctx.stroke()
    ctx.setLineDash([])

    // Similarity label at midpoint
    if (link.similarity !== null && link.similarity !== undefined) {
      const mx = (link.source.x + link.target.x) / 2
      const my = (link.source.y + link.target.y) / 2
      ctx.font         = '9px Inter, system-ui, sans-serif'
      ctx.fillStyle    = style.color
      ctx.textAlign    = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(`${Math.round(link.similarity * 100)}%`, mx, my - 7)
    }
  }, [])

  // ── Node click ────────────────────────────────────────────────────────
  const handleNodeClick = useCallback((node) => {
    setSelectedNode((prev) => (prev?.id === node.id ? null : node))
  }, [])

  // ── Viewport fit helper — zooms to fit then clamps to max 1.2 ─────────
  const fitViewport = useCallback(() => {
    const fg = graphRef.current
    if (!fg) return
    fg.zoomToFit(400, 80)
    // After the transition settles, clamp zoom so small graphs don't over-zoom
    setTimeout(() => {
      const current = graphRef.current?.zoom()
      if (current && current > 1.2) graphRef.current?.zoom(1.0, 250)
    }, 450)
  }, [])

  // ── Trigger viewport fit whenever graph data first appears ────────────
  useEffect(() => {
    if (!graphData?.nodes?.length) return
    // Small delay lets ForceGraph2D finish mounting before we touch the camera
    const t = setTimeout(fitViewport, 150)
    return () => clearTimeout(t)
  }, [graphData, fitViewport])

  // ── Zoom controls ─────────────────────────────────────────────────────
  function zoomIn()  { graphRef.current?.zoom(graphRef.current.zoom() * 1.3, 300) }
  function zoomOut() { graphRef.current?.zoom(graphRef.current.zoom() / 1.3, 300) }
  function zoomFit() { fitViewport() }

  // ── Render ─────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col h-full">

      {/* ── Page header ── */}
      <div className="px-8 pt-8 pb-5 shrink-0">
        <div className="flex items-center gap-3 mb-2">
          <div
            className="flex items-center justify-center w-9 h-9 rounded-lg"
            style={{
              background: 'rgba(83,74,183,0.15)',
              border:     '1px solid rgba(83,74,183,0.3)',
            }}
          >
            <GitFork size={18} style={{ color: 'var(--accent-violet)' }} />
          </div>
          <h1 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
            Evidence Graph
          </h1>
        </div>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Semantic and temporal relationships between retrieved intelligence sources.
          Click a node to inspect.
        </p>
      </div>

      {/* ── Graph area — takes remaining height ── */}
      <div className="flex-1 px-8 pb-8 min-h-0">
        <div
          ref={containerRef}
          className="relative w-full h-full rounded-xl overflow-hidden"
          style={{
            background: 'var(--bg-elevated)',
            border:     '1px solid var(--border)',
            minHeight:  400,
          }}
        >

          {/* ── Loading state ── */}
          {isLoading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 z-10">
              <Loader2
                size={28}
                className="animate-spin"
                style={{ color: 'var(--accent-violet)' }}
              />
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Loading evidence graph…
              </p>
            </div>
          )}

          {/* ── Error state ── */}
          {!isLoading && error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 z-10 px-8">
              <AlertCircle size={28} style={{ color: '#f87171' }} />
              <p className="text-sm font-medium" style={{ color: '#f87171' }}>
                Failed to load evidence graph
              </p>
              <p className="text-xs text-center" style={{ color: '#fca5a5' }}>
                {error}
              </p>
            </div>
          )}

          {/* ── Empty state ── */}
          {!isLoading && !error && graphData?.nodes?.length === 0 && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 z-10">
              <GitFork size={28} className="opacity-20" style={{ color: 'var(--text-secondary)' }} />
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                No evidence graph available. Run a query first.
              </p>
            </div>
          )}

          {/* ── Force graph canvas ── */}
          {!isLoading && !error && graphData?.nodes?.length > 0 && (
            <ForceGraph2D
              ref={graphRef}
              width={dimensions.w}
              height={dimensions.h}
              graphData={graphData}
              backgroundColor="transparent"

              // Nodes
              nodeCanvasObject={paintNode}
              nodeCanvasObjectMode={() => 'replace'}
              nodeLabel={(node) => `${node.label} · ${Math.round(node.confidence * 100)}% confidence`}
              onNodeClick={handleNodeClick}

              // Links
              linkCanvasObject={paintLink}
              linkCanvasObjectMode={() => 'replace'}

              // Physics — pre-stabilise positions before first render,
              // then stop quickly so zoomToFit sees settled node coordinates.
              warmupTicks={200}          // compute positions before painting
              cooldownTicks={0}          // stop simulation immediately after warmup
              d3AlphaDecay={0.05}
              d3VelocityDecay={0.4}
              nodeRelSize={6}            // base node radius in graph-space units
              linkDirectionalParticles={0}
              onEngineStop={fitViewport}

              // Zoom bounds — prevent scroll-wheel from going to extreme values
              minZoom={0.1}
              maxZoom={4}

              // Interaction
              enableNodeDrag
              enablePanInteraction
              enableZoomInteraction
            />
          )}

          {/* ── Zoom controls ── */}
          {!isLoading && !error && graphData?.nodes?.length > 0 && (
            <div
              className="absolute top-4 right-4 flex flex-col gap-1.5 z-10"
              style={{ pointerEvents: selectedNode ? 'none' : 'auto' }}
            >
              {[
                { Icon: ZoomIn,    fn: zoomIn,   title: 'Zoom in'  },
                { Icon: ZoomOut,   fn: zoomOut,  title: 'Zoom out' },
                { Icon: Maximize2, fn: zoomFit,  title: 'Fit graph' },
              ].map(({ Icon, fn, title }) => (
                <button
                  key={title}
                  onClick={fn}
                  title={title}
                  className="flex items-center justify-center w-8 h-8 rounded-lg transition-colors"
                  style={{
                    background:  'rgba(13,17,23,0.85)',
                    border:      '1px solid var(--border)',
                    color:       'var(--text-secondary)',
                    backdropFilter: 'blur(6px)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color      = 'var(--text-primary)'
                    e.currentTarget.style.background = 'rgba(29,158,117,0.15)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color      = 'var(--text-secondary)'
                    e.currentTarget.style.background = 'rgba(13,17,23,0.85)'
                  }}
                >
                  <Icon size={14} />
                </button>
              ))}
            </div>
          )}

          {/* ── Graph legend ── */}
          {!isLoading && !error && graphData?.nodes?.length > 0 && (
            <GraphLegend />
          )}

          {/* ── Node detail panel (slide-over, inside graph container) ── */}
          <NodeDetailPanel
            node={selectedNode}
            onClose={() => setSelectedNode(null)}
          />

          {/* ── Click-away overlay for panel ── */}
          {selectedNode && (
            <div
              className="absolute inset-0 z-10"
              style={{ cursor: 'default' }}
              onClick={(e) => {
                // Only close if clicking the overlay itself, not the panel
                if (e.target === e.currentTarget) setSelectedNode(null)
              }}
            />
          )}
        </div>
      </div>
    </div>
  )
}
