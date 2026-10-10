import { useEffect, useRef, useState } from 'react'
import { askAgent, errorText } from '../api/client'

export default function useChat(fileName) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeId, setActiveId] = useState(null) // which answer's trace is shown
  const nextId = useRef(1)
  const fileRef = useRef(fileName)

  // A different data file means a new conversation
  useEffect(() => {
    fileRef.current = fileName
    setMessages([])
    setActiveId(null)
    setLoading(false)
  }, [fileName])

  const ask = async (question) => {
    if (!fileName || loading) return
    const askedFile = fileName

    // Send the last 6 messages (role and text only) so follow-up questions work
    const history = messages
      .filter((m) => !m.error)
      .slice(-6)
      .map(({ role, content }) => ({ role, content }))

    setMessages((prev) => [...prev, { id: nextId.current++, role: 'user', content: question }])
    setActiveId(null)
    setLoading(true)

    try {
      const data = await askAgent(question, askedFile, history)
      if (fileRef.current !== askedFile) return // the user switched files meanwhile
      const id = nextId.current++
      setMessages((prev) => [
        ...prev,
        {
          id,
          role: 'assistant',
          content: data.answer || 'The agent did not return an answer. Try rephrasing the question.',
          charts: data.charts || [],
          steps: data.steps || [],
          llmCalls: data.llm_calls,
          latencyMs: data.latency_ms,
        },
      ])
      setActiveId(id)
    } catch (e) {
      if (fileRef.current !== askedFile) return
      setMessages((prev) => [
        ...prev,
        {
          id: nextId.current++,
          role: 'assistant',
          error: true,
          content: errorText(e, 'Could not reach the agent. Check that the backend is running.'),
        },
      ])
    } finally {
      if (fileRef.current === askedFile) setLoading(false)
    }
  }

  const clear = () => {
    setMessages([])
    setActiveId(null)
  }

  return { messages, loading, activeId, setActiveId, ask, clear }
}