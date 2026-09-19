import Link from 'next/link'
import { Compass, Loader2, RefreshCw, ServerCrash } from 'lucide-react'
import { ThemeToggle } from '@/components/layout/ThemeToggle'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { gradientBg } from './constants'
import type { Status } from './types'

export function StatusScreen({ status, message, onRetry }: { status: Status; message: string; onRetry: () => void }) {
  return (
    <div className={cn('flex h-svh flex-col text-foreground', gradientBg)}>
      <header className="border-b border-border">
        <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2 font-semibold">
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
              <Button variant="outline" nativeButton={false} render={<Link href="/" />}>
                Back home
              </Button>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
