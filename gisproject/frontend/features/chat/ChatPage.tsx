'use client'

import { OlMap } from '@/components/map/OlMap'
import { cn } from '@/lib/utils'
import { useSessionStore } from '@/store/session'
import { ChatHeader } from './ChatHeader'
import { ChatPanel } from './ChatPanel'
import { StatusScreen } from './StatusScreen'
import { gradientBg } from './constants'
import { useChatSocket } from './useChatSocket'
import { useReadySession } from './useReadySession'

function wsUrlFor(sessionId: string): string {
  return `${process.env.NEXT_PUBLIC_WS_URL}/api/ws/start/${sessionId}`
}

/** Main layout: navbar on top (always visible), map on the left, chat on the right. */
export function ChatPage() {
  const { status, message, retry } = useReadySession()
  const sessionId = useSessionStore((s) => s.sessionId)
  const chat = useChatSocket(status === 'ready' && sessionId ? wsUrlFor(sessionId) : '')

  return (
    <div className={cn('flex h-svh flex-col text-foreground', gradientBg)}>
      <ChatHeader isConnected={chat.isConnected} />

      {status !== 'ready' ? (
        <StatusScreen status={status} message={message} onRetry={retry} />
      ) : (
        <main className="grid min-h-0 flex-1 grid-rows-[35%_1fr] border-t border-border md:grid-cols-[3fr_2fr] md:grid-rows-1">
          <section className="min-h-0 min-w-0 border-b border-border md:border-r md:border-b-0">
            <OlMap />
          </section>
          <section className="flex min-h-0 min-w-0 flex-col">
            <ChatPanel chat={chat} />
          </section>
        </main>
      )}
    </div>
  )
}
