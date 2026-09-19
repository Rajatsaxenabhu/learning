export type Message = { id: number; role: 'user' | 'assistant' | 'error'; text: string }

export type ReadyResponse = { status: string; session_id: string; model: string }

export type Status = 'checking' | 'ready' | 'error'
