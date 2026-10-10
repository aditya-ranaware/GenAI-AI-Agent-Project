import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { chartUrl } from '../api/client'

export default function Answer({ message, isActive, onShowTrace, onMediaLoad }) {
  const stepCount = message.steps?.length ?? 0

  return (
    <article className={`answer ${message.error ? 'is-error' : ''} ${isActive ? 'is-active' : ''}`}>
      <div className="md">
            <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            table: (props) => (
              <div className="table-scroll">
                <table {...props} />
              </div>
            ),
          }}
        >
          {message.content}
        </ReactMarkdown>
      </div>

      {message.charts?.map((name) => (
        <img key={name} className="answer-chart" src={chartUrl(name)} alt="Chart created by the agent" onLoad={onMediaLoad} />
      ))}

      {message.steps && (
        <footer className="answer-foot">
          <span>
            {stepCount === 0 ? 'Answered without tools' : `${stepCount} ${stepCount === 1 ? 'step' : 'steps'}`}
          </span>
          <span>{(message.latencyMs / 1000).toFixed(1)} s</span>
          {stepCount > 0 && (
            <button
              type="button"
              className="link-btn"
              aria-pressed={isActive}
              onClick={() => onShowTrace(message.id)}
            >
              {isActive ? 'Trace shown' : 'Show trace'}
            </button>
          )}
        </footer>
      )}
    </article>
  )
}