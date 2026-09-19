import { useCallback, useEffect, useRef, useState } from 'react'
import { toast } from 'react-toastify'
import { useWebSocket } from '@/services/websocket'
import type { Message } from './types'

/** Owns the chat transcript: turns websocket frames into messages, token usage and tool approvals. */
export function useChatSocket(url: string) {
  const { isConnected, messages: wsMessages, sendMessage } = useWebSocket(url)
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [totalTokens, setTotalTokens] = useState(0)
  const [approval, setApproval] = useState<Record<string, unknown> | null>(null)
  const [streaming, setStreaming] = useState(false)
  const nextId = useRef(0)
  const processed = useRef(0)
  const streamingId = useRef<number | null>(null)

  const add = useCallback(
    (role: Message['role'], text: string) => setMessages((m) => [...m, { id: nextId.current++, role, text }]),
    [],
  )

  useEffect(() => {
    if (wsMessages.length < processed.current) processed.current = 0
    for (const raw of wsMessages.slice(processed.current)) {
      let data: Record<string, unknown>
      try {
        data = JSON.parse(raw)
      } catch {
        continue
      }
      if (data.type === 'connected') {
        setTotalTokens(Number(data.total_tokens ?? 0))
      } else if (data.type === 'usage') {
        setTotalTokens(Number(data.total ?? 0))
      } else if (data.type === 'token') {
        const text = String(data.content ?? '')
        if (streamingId.current === null) {
          const id = nextId.current++
          streamingId.current = id
          setStreaming(true)
          setMessages((m) => [...m, { id, role: 'assistant', text }])
        } else {
          const id = streamingId.current
          setMessages((m) => m.map((msg) => (msg.id === id ? { ...msg, text: msg.text + text } : msg)))
        }
      } else if (data.type === 'done') {
        streamingId.current = null
        setStreaming(false)
        setLoading(false)
      } else if (data.type === 'error') {
        streamingId.current = null
        setStreaming(false)
        add('error', String(data.detail ?? 'Something went wrong'))
        setLoading(false)
      } else if (data.type === 'tool_approval') {
        setApproval(data)
      }
    }
    processed.current = wsMessages.length
  }, [wsMessages, add])

  useEffect(() => {
    if (!isConnected) {
      streamingId.current = null
      setStreaming(false)
      setLoading(false)
      setApproval(null)
    }
  }, [isConnected])

  const answerApproval = (approve: boolean) => {
    sendMessage(JSON.stringify({ approve }))
    setApproval(null)
  }

  /** Returns true when the message was sent. */
  const send = (text: string, display = text, datasetId?: string): boolean => {
    if (loading) return false
    if (!isConnected) {
      toast.error('Not connected yet, try again in a moment')
      return false
    }
    add('user', display)
    setLoading(true)
    sendMessage(JSON.stringify({ message: text, dataset_id: datasetId }))
    return true
  }

  return { isConnected, messages, loading, streaming, totalTokens, approval, answerApproval, send }
}
