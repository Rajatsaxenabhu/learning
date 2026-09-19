import Markdown, { type Components } from 'react-markdown'
import { Boxes, Compass, Grid3x3, Layers, Loader2, Map, Ruler, ScanLine, RefreshCw, SendHorizontal, ServerCrash, type LucideIcon } from 'lucide-react'
import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import { Link } from 'react-router'
import { toast } from 'react-toastify'
import { ThemeToggle } from '@/components/layout/ThemeToggle'
import { Button } from '@/components/ui/button'
import { api } from '@/services/api'
import { useWebSocket } from '@/services/websocket'
import { cn } from '@/lib/utils'
import { useSessionStore } from '@/store/session'

function wsUrlFor(sessionId: string): string {
  return `${import.meta.env.VITE_WS_URL}/api/ws/start/${sessionId}`
}

type ReadyResponse = { status: string; session_id: string; model: string }

type Message = { id: number; role: 'user' | 'assistant' | 'error'; text: string }

const gradientBg =
  'bg-[radial-gradient(60rem_40rem_at_15%_-10%,oklch(0.93_0.06_165/0.55),transparent),radial-gradient(50rem_35rem_at_100%_0%,oklch(0.92_0.05_240/0.5),transparent)] dark:bg-[radial-gradient(60rem_40rem_at_15%_-10%,oklch(0.45_0.1_165/0.28),transparent),radial-gradient(50rem_35rem_at_100%_0%,oklch(0.4_0.12_260/0.25),transparent)] bg-background'

const mdComponents: Components = {
  p: (props) => <p className="my-2 first:mt-0 last:mb-0" {...props} />,
  ul: (props) => <ul className="my-2 list-disc space-y-1 pl-5" {...props} />,
  ol: (props) => <ol className="my-2 list-decimal space-y-1 pl-5" {...props} />,
  strong: (props) => <strong className="font-semibold" {...props} />,
  code: (props) => <code className="rounded-md bg-foreground/10 px-1.5 py-0.5 font-mono text-[13px]" {...props} />,
  pre: (props) => <pre className="my-3 overflow-auto rounded-xl bg-foreground/[0.06] p-4 text-[13px]" {...props} />,
  a: (props) => <a className="text-emerald-400 underline underline-offset-2" target="_blank" rel="noreferrer" {...props} />,
}

const capabilities: { icon: LucideIcon; title: string; hint: string; prompt: string }[] = [
  { icon: Ruler, title: 'Geometry', hint: 'Area, buffer, intersect', prompt: 'Buffer this point by 500 m and calculate the area' },
  { icon: Map, title: 'Projection', hint: 'CRS and UTM zones', prompt: 'Which UTM zone is longitude 77.2, latitude 28.6 in?' },
  { icon: Layers, title: 'Vector data', hint: 'Layers, filters, queries', prompt: 'List the layers and schema of my vector file' },
  { icon: ScanLine, title: 'Raster info', hint: 'Metadata, CRS, bands', prompt: 'Show the metadata and band info of my raster' },
  { icon: Grid3x3, title: 'Raster stats', hint: 'Histogram, percentiles', prompt: 'Calculate statistics and a histogram for my raster' },
  { icon: Boxes, title: 'Processing', hint: 'Clip, reproject, merge', prompt: 'Clip my raster to a polygon and reproject it to EPSG:4326' },
]

type Status = 'checking' | 'ready' | 'error'

function StatusScreen({ status, message, onRetry }: { status: Status; message: string; onRetry: () => void }) {
  return (
    <div className={cn('flex h-svh flex-col text-foreground', gradientBg)}>
      <header className="border-b border-border">
        <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-4">
          <Link to="/" className="flex items-center gap-2 font-semibold">
            <Compass className="size-5 text-emerald-500" />
            GeoAgent
          </Link>
          <ThemeToggle />
        </div>
      </header>
      <main className="flex flex-1 flex-col items-center justify-center gap-4 px-4 text-center">
        {status === 'checking' ? (
          <>
            <Loader2 className="size-8 animate-spin text-emerald-500" />
            <p className="text-muted-foreground">Checking that the model is ready…</p>
          </>
        ) : (
          <>
            <ServerCrash className="size-10 text-destructive" />
            <h1 className="text-2xl font-semibold">Model is not ready</h1>
            <p className="max-w-md text-muted-foreground">{message}</p>
            <div className="flex gap-2">
              <Button onClick={onRetry}>
                <RefreshCw /> Try again
              </Button>
              <Button variant="outline" render={<Link to="/" />}>
                Back home
              </Button>
            </div>
          </>
        )}
      </main>
    </div>
  )
}

export default function AppPage() {
  const [status, setStatus] = useState<Status>('checking')
  const [statusMessage, setStatusMessage] = useState('')
  const [attempt, setAttempt] = useState(0)
  const model = useSessionStore((s) => s.model)
  const sessionId = useSessionStore((s) => s.sessionId)
  const setSession = useSessionStore((s) => s.setSession)
  const { isConnected, messages: wsMessages, sendMessage } = useWebSocket(status === 'ready' && sessionId ? wsUrlFor(sessionId) : '')

  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const nextId = useRef(0)
  const processed = useRef(0)
  const streamingId = useRef<number | null>(null)
  const [totalTokens, setTotalTokens] = useState(0)
  const [approval, setApproval] = useState<Record<string, unknown> | null>(null)

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
        setStatusMessage(msg)
        setStatus('error')
        toast.error(`Model not ready: ${msg}`, { toastId: 'ready-error' })
      })
    return () => controller.abort()
  }, [attempt, setSession])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

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
          setMessages((m) => [...m, { id, role: 'assistant', text }])
        } else {
          const id = streamingId.current
          setMessages((m) => m.map((msg) => (msg.id === id ? { ...msg, text: msg.text + text } : msg)))
        }
      } else if (data.type === 'done') {
        streamingId.current = null
        setLoading(false)
      } else if (data.type === 'error') {
        streamingId.current = null
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
      setLoading(false)
      setApproval(null)
    }
  }, [isConnected])

  function answerApproval(approve: boolean) {
    sendMessage(JSON.stringify({ approve }))
    setApproval(null)
  }

  function submit(query: string) {
    const q = query.trim()
    if (!q || loading) return
    if (!isConnected) {
      toast.error('Not connected yet, try again in a moment')
      return
    }
    setInput('')
    add('user', q)
    setLoading(true)
    sendMessage(JSON.stringify({ message: q }))
  }

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    submit(input)
  }

  if (status !== 'ready') {
    return <StatusScreen status={status} message={statusMessage} onRetry={() => setAttempt((a) => a + 1)} />
  }

  return (
    <div className={cn('flex h-svh flex-col text-foreground', gradientBg)}>
      <header>
        <div className="mx-auto flex h-16 max-w-3xl items-center justify-between px-4">
          <Link to="/" className="flex items-center gap-2.5 font-semibold tracking-tight">
            <span className="grid size-8 place-items-center rounded-full bg-gradient-to-br from-emerald-400 to-sky-400 text-white">
              <Compass className="size-4" />
            </span>
            GeoAgent
          </Link>
          <div className="flex items-center gap-1">
            <div className="flex items-center gap-2 rounded-full px-3 py-1.5 text-sm text-muted-foreground transition hover:bg-foreground/5">
              <span
                title={isConnected ? 'Connected' : 'Connecting…'}
                className={cn('size-1.5 shrink-0 rounded-full', isConnected ? 'bg-emerald-400' : 'bg-muted-foreground/40')}
              />
              <select
                value={model ?? ''}
                onChange={(e) => setSession(useSessionStore.getState().sessionId ?? '', e.target.value)}
                aria-label="Select model"
                className="max-w-40 cursor-pointer truncate bg-transparent outline-none"
              >
                {model && <option value={model}>{model}</option>}
              </select>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

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
                    onClick={() => setInput(prompt)}
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
                <Button size="sm" onClick={() => answerApproval(true)}>
                  Allow
                </Button>
                <Button size="sm" variant="ghost" onClick={() => answerApproval(false)}>
                  Deny
                </Button>
              </div>
            </div>
          )}

          {loading && !approval && streamingId.current === null && (
            <div className="flex items-center gap-3">
              <span className="size-6 shrink-0 animate-pulse rounded-full bg-gradient-to-br from-emerald-400 to-sky-400" />
              <span className="text-sm text-muted-foreground">Thinking…</span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </main>

      <form onSubmit={onSubmit} className="px-4 pb-4">
        <div className="mx-auto flex max-w-3xl items-center gap-2 rounded-[1.75rem] bg-foreground/[0.06] p-2 pl-6 ring-1 ring-foreground/10 transition focus-within:bg-foreground/[0.08] focus-within:ring-emerald-400/50">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about a layer, raster or coordinate…"
            className="h-12 flex-1 bg-transparent text-[15px] outline-none placeholder:text-muted-foreground/70"
          />
          <Button
            type="submit"
            size="icon"
            className="size-10 rounded-full border-0 bg-gradient-to-br from-emerald-400 to-sky-400 text-white hover:opacity-90 disabled:opacity-30"
            disabled={loading || !input.trim()}
            aria-label="Send"
          >
            <SendHorizontal />
          </Button>
        </div>
        {totalTokens > 0 && (
          <p className="mt-2 text-center text-[11px] text-muted-foreground/70 tabular-nums">
            {totalTokens.toLocaleString()} tokens
          </p>
        )}
      </form>
    </div>
  )
}
