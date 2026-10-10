import axios from 'axios'

// In deployment, set VITE_API_URL to your hosted backend address
export const API_BASE =
  import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '/api' : 'http://127.0.0.1:8000/api')
const api = axios.create({ baseURL: API_BASE })

export const getFiles = () => api.get('/files').then((r) => r.data.files)

export const uploadFile = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/files/upload', form).then((r) => r.data)
}

export const deleteFile = (name) =>
  api.delete(`/files/${encodeURIComponent(name)}`).then((r) => r.data)

export const askAgent = (question, fileName, history = []) =>
  api.post('/ask', { question, file_name: fileName, history }).then((r) => r.data)

export const chartUrl = (name) => `${API_BASE}/charts/${name}`

// Turn a failed request into a readable message
export const errorText = (e, fallback) =>
  typeof e.response?.data?.detail === 'string' ? e.response.data.detail : fallback