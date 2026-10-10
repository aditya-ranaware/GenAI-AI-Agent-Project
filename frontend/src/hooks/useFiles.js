import { useCallback, useEffect, useState } from 'react'
import { deleteFile, errorText, getFiles, uploadFile } from '../api/client'

export default function useFiles() {
  const [files, setFiles] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  // Reload the list. Keep the current selection if it still exists.
  const refresh = useCallback(async (preferred) => {
    try {
      const list = await getFiles()
      setFiles(list)
      setSelected((current) => {
        if (preferred && list.includes(preferred)) return preferred
        if (list.includes(current)) return current
        return list[0] ?? null
      })
      setError('')
    } catch {
      setError('Cannot reach the server. Check that the backend is running.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const upload = async (file) => {
    setUploading(true)
    setError('')
    try {
      const data = await uploadFile(file)
      await refresh(data.file) // select the file that was just uploaded
    } catch (e) {
      setError(errorText(e, 'Upload failed. Check the file and try again.'))
    } finally {
      setUploading(false)
    }
  }

  const remove = async (name) => {
    setError('')
    try {
      await deleteFile(name)
      await refresh()
    } catch (e) {
      setError(errorText(e, 'Could not delete the file.'))
    }
  }

  return { files, selected, setSelected, loading, uploading, error, upload, remove }
}