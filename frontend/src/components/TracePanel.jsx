const sentence = (text) => text.charAt(0).toUpperCase() + text.slice(1)

// Plain-English description of what a tool call did
function describe(step) {
  const a = step.args || {}
  switch (step.tool) {
    case 'get_schema':
      return 'Read the column names, types and a few sample rows.'
    case 'query_data': {
      const parts = []
      if (a.filters?.length) parts.push(`filtered by ${a.filters.map((f) => `${f.column} ${f.op} ${f.value}`).join(' and ')}`)
      if (a.group_by?.length) parts.push(`grouped by ${a.group_by.join(', ')}`)
      if (a.aggregations?.length) parts.push(`calculated ${a.aggregations.map((x) => `${x.function} of ${x.column}`).join(', ')}`)
      if (a.sort_by) parts.push(`sorted by ${a.sort_by}`)
      return `${sentence(parts.length ? parts.join(', ') : 'read rows from the file')}.`
    }
    case 'make_chart':
      return `Drew a ${a.chart_type} chart of ${a.aggregation || 'sum'} of ${a.y} by ${a.x}.`
    case '(retry)':
      return 'The model sent an invalid tool call, so the agent asked it to try again.'
    default:
      return `Called ${step.tool}.`
  }
}

function errorMessage(step) {
  if (step.tool === '(retry)') return 'Invalid tool call'
  try {
    const parsed = JSON.parse(step.result)
    return typeof parsed.error === 'string' ? parsed.error : null
  } catch {
    return step.result?.startsWith('{"error"') ? step.result : null
  }
}

function Step({ step, index }) {
  const error = errorMessage(step)
  return (
    <li className={`trace-step ${error ? 'is-error' : 'is-ok'}`}>
      <span className="trace-num" aria-hidden="true">
        {index + 1}
      </span>
      <div className="trace-body">
        <div className="trace-head">
          <span className="trace-tool">{step.tool}</span>
          <span className="trace-status">{error ? 'Error' : 'Done'}</span>
        </div>
        <p className="trace-text">{error ? `The tool returned an error: ${error}` : describe(step)}</p>
        {step.tool !== '(retry)' && (
          <details className="trace-details">
            <summary>Input and result</summary>
            <div className="trace-label">Input</div>
            <pre>{JSON.stringify(step.args, null, 2)}</pre>
            <div className="trace-label">Result (first 300 characters)</div>
            <pre>{step.result}</pre>
          </details>
        )}
      </div>
    </li>
  )
}

export default function TracePanel({ message, loading, open, onClose }) {
const steps = message?.steps ?? []

  return (
       <aside className={`app-trace ${open ? 'is-open' : ''}`} aria-label="Agent trace">
      <div className="panel-head">
        <h2 className="panel-title">Agent trace</h2>
        <button type="button" className="btn-icon trace-close" aria-label="Close agent trace" onClick={onClose}>
          <i className="bi bi-x-lg" aria-hidden="true" />
        </button>
      </div>

      {loading && (
        <p className="trace-note" role="status">
          <span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />
          The agent is working. Its steps appear here when it finishes.
        </p>
      )}

      {!loading && !message && (
        <p className="trace-note">
          Ask a question and the agent's steps appear here, so you can check how it reached the answer.
        </p>
      )}

      {!loading && message && steps.length === 0 && (
        <p className="trace-note">The agent answered without using any tools.</p>
      )}

      {!loading && steps.length > 0 && (
        <>
          <p className="trace-summary">
            {steps.length} tool {steps.length === 1 ? 'call' : 'calls'}, {message.llmCalls} model{' '}
            {message.llmCalls === 1 ? 'call' : 'calls'}, {(message.latencyMs / 1000).toFixed(1)} s
          </p>
          <ol className="trace-list">
            {steps.map((step, i) => (
              <Step key={i} step={step} index={i} />
            ))}
          </ol>
        </>
      )}
    </aside>
  )
}