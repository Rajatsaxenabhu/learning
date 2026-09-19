import Link from 'next/link'
import { Compass } from 'lucide-react'
import { ThemeToggle } from '@/components/layout/ThemeToggle'
import { cn } from '@/lib/utils'
import { useSessionStore } from '@/store/session'

export function ChatHeader({ isConnected }: { isConnected: boolean }) {
  const model = useSessionStore((s) => s.model)
  const setSession = useSessionStore((s) => s.setSession)

  return (
    <header>
      <div className="mx-auto flex h-16 max-w-3xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2.5 font-semibold tracking-tight">
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
  )
}
