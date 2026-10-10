import { useRef, useState } from 'react'

export default function DataRail({ files, selected, loading, uploading, error, open, onClose, onSelect, onUpload, onRemove }) {
const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)

  const pick = (list) => {
    const file = list?.[0]
    if (file) onUpload(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    pick(e.dataTransfer.files)
  }

  const confirmDelete = (name) => {
    if (window.confirm(`Delete "${name}"? This cannot be undone.`)) onRemove(name)
  }

  return (
    <aside
          className={`app-rail ${open ? 'is-open' : ''} ${dragging ? 'is-dragging' : ''}`}
    onDragOver={(e) => {
        e.preventDefault()
        setDragging(true)
      }}
      onDragLeave={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget)) setDragging(false)
      }}
      onDrop={handleDrop}
    >
      <div className="panel-head">
        <h2 className="panel-title">Data files</h2>
        <button type="button" className="btn-icon rail-close" aria-label="Close data files" onClick={onClose}>
          <i className="bi bi-x-lg" aria-hidden="true" />
        </button>
      </div>
      <button
        type="button"
        className="btn btn-outline-primary w-100"
        disabled={uploading}
        onClick={() => inputRef.current.click()}
      >
        {uploading ? (
          <>
            <span className="spinner-border spinner-border-sm me-2" aria-hidden="true" />
            Reading file…
          </>
        ) : (
          <>
            <i className="bi bi-plus-lg me-2" aria-hidden="true" />
            Upload CSV
          </>
        )}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,text/csv"
        hidden
        onChange={(e) => {
          pick(e.target.files)
          e.target.value = ''
        }}
      />
      <p className="rail-hint">Or drop a file anywhere in this panel. Up to 5 MB.</p>

      {error && (
        <div className="alert alert-danger py-2 small" role="alert">
          {error}
        </div>
      )}

      {!loading && files.length === 0 && !error && (
        <p className="rail-empty">No data yet. Upload a CSV and ask questions about it in plain English.</p>
      )}

      <ul className="file-list">
        {files.map((name) => (
          <li key={name} className={`file-item ${name === selected ? 'is-active' : ''}`}>
            <button
              type="button"
              className="file-select"
              aria-pressed={name === selected}
              onClick={() => onSelect(name)}
            >
              <i className="bi bi-file-earmark-spreadsheet" aria-hidden="true" />
              <span className="file-name" title={name}>
                {name}
              </span>
            </button>
            <button
              type="button"
              className="btn-icon"
              aria-label={`Delete ${name}`}
              onClick={() => confirmDelete(name)}
            >
              <i className="bi bi-trash3" aria-hidden="true" />
            </button>
          </li>
        ))}
      </ul>
    </aside>
  )
}