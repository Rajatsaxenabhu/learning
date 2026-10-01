import Link from 'next/link'
import { RefreshCw, ServerCrash } from 'lucide-react'
import { GeoLoader } from '@/components/layout/GeoLoader'
import { Button } from '@/components/ui/button'
import type { Status } from './types'

export function StatusScreen({ status, message, onRetry }: { status: Status; message: string; onRetry: () => void }) {
  return (
    <>
      <main className="flex flex-1 flex-col items-center justify-center gap-4 px-4 text-center">
        {status === 'checking' ? (
          <>
            <GeoLoader />
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
    </>
  )
}
