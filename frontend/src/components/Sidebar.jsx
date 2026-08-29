import { NavLink } from 'react-router-dom'
import { Upload, Search, GitFork, Layers } from 'lucide-react'
import { cn } from '../lib/cn'

const NAV_ITEMS = [
  { to: '/upload',   label: 'Upload',   Icon: Upload,   title: 'Ingest documents' },
  { to: '/query',    label: 'Query',    Icon: Search,   title: 'Query the knowledge base' },
  { to: '/evidence', label: 'Evidence', Icon: GitFork,  title: 'Explore the evidence graph' },
]

export default function Sidebar() {
  return (
    <aside className="flex flex-col w-60 min-h-screen shrink-0 border-r"
           style={{ background: 'var(--bg-surface)', borderColor: 'var(--border)' }}>

      {/* ── Brand ── */}
      <div className="flex items-center gap-3 px-5 py-5 border-b" style={{ borderColor: 'var(--border)' }}>
        <div className="flex items-center justify-center w-8 h-8 rounded-lg glow-teal"
             style={{ background: 'var(--accent-teal)' }}>
          <Layers size={16} className="text-white" />
        </div>
        <div>
          <span className="text-base font-bold tracking-widest text-gradient-teal">AQILA</span>
          <p className="text-xs leading-none mt-0.5" style={{ color: 'var(--text-muted)' }}>
            Intelligence Analysis
          </p>
        </div>
      </div>

      {/* ── Navigation ── */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ to, label, Icon, title }) => (
          <NavLink
            key={to}
            to={to}
            title={title}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                isActive
                  ? 'text-white glow-teal'
                  : 'hover:bg-white/5',
              )
            }
            style={({ isActive }) => isActive
              ? { background: 'rgba(29,158,117,0.18)', color: '#43ce9e' }
              : { color: 'var(--text-secondary)' }
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={17} strokeWidth={isActive ? 2.2 : 1.8} />
                {label}
                {isActive && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full"
                        style={{ background: 'var(--accent-teal)' }} />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* ── Footer ── */}
      <div className="px-5 py-4 border-t text-xs" style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
        SIH 2026 · M3 Frontend
      </div>
    </aside>
  )
}
