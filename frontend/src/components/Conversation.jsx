import { useEffect, useRef, useState } from 'react'
import Answer from './Answer'

const STARTERS = [
  'Give me a quick summary of this data',
  'Which category has the highest total?',
  'Plot the main trend as a chart',
]

export default function Conversation({ fileName, messages, loading, activeId, onAsk, onShowTrace, onClear }) {
  const [text, setText] = useState('')
  const endRef = useRef(null)
  const inputRef = useRef(null)
  const ready = Boolean(fileName)

  // Braces matter: the function must not return anything, because React treats a returned value as cleanup
  const scrollToEnd = () => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }

  // Keep the newest message in view
  useEffect(() => {
    scrollToEnd()
  }, [messages, loading])

  const resize = (el) => {
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`
  }

  const send = (question) => {
    const q = question.trim()
    if (!q || loading || !ready) return
    setText('')
    if (inputRef.current) inputRef.current.style.height = 'auto'
    onAsk(q)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send(text)
    }
  }

  return (
    <main className="app-main">
      <div className="convo-scroll">
        <div className="convo-column">
          {messages.length === 0 && !loading && (
            <div className="convo-empty">
              <h2>{ready ? `Ask anything about ${fileName}` : 'Upload a CSV to begin'}</h2>
              <p>
                {ready
                  ? 'The agent looks at your data, runs the numbers, and shows every step it took.'
                  : 'Use the panel on the left. Then ask your questions in plain English.'}
              </p>
              {ready && (
                <div className="starters">
                  {STARTERS.map((s) => (
                    <button key={s} type="button" className="starter" onClick={() => send(s)}>
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {messages.map((m) =>
            m.role === 'user' ? (
              <div key={m.id} className="ask">
                <div className="ask-bubble">{m.content}</div>
              </div>
            ) : (
              <Answer
                key={m.id}
                message={m}
                isActive={m.id === activeId}
                onShowTrace={onShowTrace}
                onMediaLoad={scrollToEnd}
              />
            ),
          )}

          {loading && (
            <div className="working" role="status">
              <span className="spinner-border spinner-border-sm" aria-hidden="true" />
              Analyzing your data…
            </div>
          )}
          <div ref={endRef} />
        </div>
      </div>

      <div className="composer-wrap">
        <div className="convo-column">
          <div className="composer">
            <textarea
              ref={inputRef}
              rows={1}
              value={text}
              disabled={!ready}
              placeholder={ready ? 'Ask a question about your data' : 'Upload a CSV first'}
              aria-label="Your question"
              onChange={(e) => {
                setText(e.target.value)
                resize(e.target)
              }}
              onKeyDown={handleKeyDown}
            />
            <button
              type="button"
              className="btn btn-primary composer-send"
              disabled={!text.trim() || loading || !ready}
              onClick={() => send(text)}
            >
              Ask
            </button>
          </div>
          <div className="composer-foot">
            <span>Enter to send, Shift+Enter for a new line</span>
            {messages.length > 0 && (
              <button type="button" className="link-btn" onClick={onClear}>
                Clear conversation
              </button>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}