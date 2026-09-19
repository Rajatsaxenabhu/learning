import { create } from 'zustand'

type SessionState = {
  sessionId: string | null
  model: string | null
  setSession: (sessionId: string, model: string) => void
  clearSession: () => void
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  model: null,
  setSession: (sessionId, model) => set({ sessionId, model }),
  clearSession: () => set({ sessionId: null, model: null }),
}))
