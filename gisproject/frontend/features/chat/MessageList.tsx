import Markdown from 'react-markdown'
import { useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { capabilities } from './constants'
import { mdComponents } from './markdown'
import type { Message } from './types'

type Props = {
  messages: Message[]
  loading: boolean
  streaming: boolean
  approval: Record<string, unknown> | null
  onAnswerApproval: (approve: boolean) => void
  onPickPrompt: (prompt: string) => void
}

export function MessageList({ messages, loading, streaming, approval, onAnswerApproval, onPickPrompt }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  return (
    <main className="flex-1 overflow-y-auto">
      <div className="mx-auto flex max-w-3xl flex-col gap-8 px-4 pt-6 pb-10">
        {messages.length === 0 && (
          <div className="mt-[12vh] text-center">
            <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
              Where shall we{' '}
              <span className="bg-gradient-to-r from-emerald-400 via-sky-400 to-violet-400 bg-clip-text text-transparent">
                map
              </span>{' '}
              today?
            </h1>
            <div className="mx-auto mt-10 flex max-w-xl flex-wrap justify-center gap-2">
              {capabilities.map(({ icon: Icon, title, prompt }) => (
                <button
                  key={title}
                  onClick={() => onPickPrompt(prompt)}
                  className="flex items-center gap-2 rounded-full bg-foreground/[0.05] px-4 py-2 text-sm text-muted-foreground transition hover:bg-foreground/10 hover:text-foreground"
                >
                  <Icon className="size-4 text-emerald-400" />
                  {title}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) =>
          m.role === 'user' ? (
            <div key={m.id} className="flex justify-end">
              <div className="max-w-[80%] rounded-3xl bg-foreground/[0.07] px-5 py-2.5 text-[15px] whitespace-pre-wrap">
                {m.text}
              </div>
            </div>
          ) : (
            <div key={m.id} className="flex gap-3">
              <span className="mt-0.5 size-6 shrink-0 rounded-full bg-gradient-to-br from-emerald-400 to-sky-400" />
              {m.role === 'error' ? (
                <p className="text-[15px] text-destructive">{m.text}</p>
              ) : (
                <div className="min-w-0 flex-1 text-[15px] leading-7">
                  <Markdown components={mdComponents}>{m.text.trim()}</Markdown>
                </div>
              )}
            </div>
          ),
        )}

        {approval && (
          <div className="ml-9 max-w-md rounded-2xl border border-amber-400/40 bg-amber-400/5 px-4 py-3 text-sm">
            <p className="font-medium">Allow this tool to run?</p>
            <details className="mt-1 text-xs text-muted-foreground">
              <summary className="cursor-pointer">Details</summary>
              <pre className="mt-2 max-h-40 overflow-auto rounded-xl bg-foreground/5 p-3 whitespace-pre-wrap">
                {JSON.stringify(Object.fromEntries(Object.entries(approval).filter(([k]) => k !== 'type')), null, 2)}
              </pre>
            </details>
            <div className="mt-3 flex gap-2">
              <Button size="sm" onClick={() => onAnswerApproval(true)}>
                Allow
              </Button>
              <Button size="sm" variant="ghost" onClick={() => onAnswerApproval(false)}>
                Deny
              </Button>
            </div>
          </div>
        )}

        {loading && !approval && !streaming && (
          <div className="flex items-center gap-3">
            <span className="size-6 shrink-0 animate-pulse rounded-full bg-gradient-to-br from-emerald-400 to-sky-400" />
            <span className="text-sm text-muted-foreground">Thinking…</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </main>
  )
}
