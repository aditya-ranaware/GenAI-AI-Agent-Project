import { useEffect, useState } from 'react'
import Conversation from './components/Conversation'
import DataRail from './components/DataRail'
import TracePanel from './components/TracePanel'
import useChat from './hooks/useChat'
import useFiles from './hooks/useFiles'

export default function App() {
  const data = useFiles()
  const chat = useChat(data.selected)
  const traceMessage = chat.messages.find((m) => m.id === chat.activeId)

  // On small screens the side panels are drawers. On large screens these do nothing.
  const [railOpen, setRailOpen] = useState(false)
  const [traceOpen, setTraceOpen] = useState(false)

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') {
        setRailOpen(false)
        setTraceOpen(false)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  return (
    <div className="app-shell">
      <header className="app-topbar">
        <div className="topbar-left">
          <button
            type="button"
            className="topbar-btn topbar-menu"
            aria-label="Open data files"
            onClick={() => setRailOpen(true)}
          >
            <i className="bi bi-list" aria-hidden="true" />
          </button>
          <div className="app-brand">
            <span className="app-brand-mark">
              <i className="bi bi-graph-up-arrow" aria-hidden="true" />
            </span>
            Data Analyst Agent
          </div>
        </div>

        <div className="topbar-right">
          {data.selected && (
            <span className="active-file">
              <i className="bi bi-file-earmark-spreadsheet" aria-hidden="true" />
              {data.selected}
            </span>
          )}
          <button type="button" className="topbar-btn topbar-trace" onClick={() => setTraceOpen(true)}>
            <i className="bi bi-diagram-3" aria-hidden="true" />
            Trace
          </button>
        </div>
      </header>

      <div className="app-body">
        <DataRail
          files={data.files}
          selected={data.selected}
          loading={data.loading}
          uploading={data.uploading}
          error={data.error}
          open={railOpen}
          onClose={() => setRailOpen(false)}
          onSelect={(name) => {
            data.setSelected(name)
            setRailOpen(false)
          }}
          onUpload={data.upload}
          onRemove={data.remove}
        />
        {railOpen && <div className="drawer-backdrop for-rail" onClick={() => setRailOpen(false)} />}

        <Conversation
          fileName={data.selected}
          messages={chat.messages}
          loading={chat.loading}
          activeId={chat.activeId}
          onAsk={chat.ask}
          onShowTrace={(id) => {
            chat.setActiveId(id)
            setTraceOpen(true) // opens the drawer on small screens
          }}
          onClear={chat.clear}
        />

        {traceOpen && <div className="drawer-backdrop for-trace" onClick={() => setTraceOpen(false)} />}
        <TracePanel
          message={traceMessage}
          loading={chat.loading}
          open={traceOpen}
          onClose={() => setTraceOpen(false)}
        />
      </div>
    </div>
  )
}