import { useEffect, useState } from 'react'
import { toast } from 'react-toastify'
import { api } from '@/services/api'
import { useSessionStore } from '@/store/session'
import type { ReadyResponse, Status } from './types'

/** Asks the backend whether the model is up and stores the session it hands back. */
export function useReadySession() {
  const [status, setStatus] = useState<Status>('checking')
  const [message, setMessage] = useState('')
  const [attempt, setAttempt] = useState(0)
  const setSession = useSessionStore((s) => s.setSession)

  useEffect(() => {
    const controller = new AbortController()
    setStatus('checking')
    api
      .get<ReadyResponse>('/api/ready', { signal: controller.signal })
      .then(({ message }) => {
        if (!message?.session_id) throw new Error('Server did not return a session')
        setSession(message.session_id, message.model)
        setStatus('ready')
      })
      .catch((e) => {
        if (controller.signal.aborted) return
        const msg = e instanceof Error ? e.message : 'Could not reach the server'
        setMessage(msg)
        setStatus('error')
        toast.error(`Model not ready: ${msg}`, { toastId: 'ready-error' })
      })
    return () => controller.abort()
  }, [attempt, setSession])

  return { status, message, retry: () => setAttempt((a) => a + 1) }
}
