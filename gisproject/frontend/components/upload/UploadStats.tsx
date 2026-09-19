import { CheckCircle2, FileUp, RotateCcw, X, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { formatBytes } from '@/lib/format'
import { cn } from '@/lib/utils'
import type { UploadProgress } from '@/services/upload'

type Props = {
  fileName: string
  status: 'uploading' | 'done' | 'error'
  progress: UploadProgress | null
  error?: string
  onCancel?: () => void
  onRetry?: () => void
  onClose?: () => void
  className?: string
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-[11px] text-muted-foreground/80">{label}</dt>
      <dd className="truncate text-sm font-medium tabular-nums">{value}</dd>
    </div>
  )
}

/** Reusable progress card: bytes uploaded to the backend, percent, speed, ETA and chunk count. */
export function UploadStats({ fileName, status, progress, error, onCancel, onRetry, onClose, className }: Props) {
  const percent = progress?.percent ?? 0
  const Icon = status === 'done' ? CheckCircle2 : status === 'error' ? XCircle : FileUp
  const iconColor = status === 'done' ? 'text-emerald-400' : status === 'error' ? 'text-destructive' : 'text-sky-400'

  return (
    <div className={cn('rounded-2xl bg-background p-3 shadow-xl ring-1 ring-foreground/10', className)}>
      <div className="flex items-center gap-3">
        <Icon className={cn('size-5 shrink-0', iconColor)} />
        <p className="min-w-0 flex-1 truncate text-sm font-medium" title={fileName}>
          {fileName}
        </p>
        <span className="text-sm font-semibold tabular-nums">{Math.floor(percent)}%</span>
        {status === 'uploading' && onCancel && (
          <Button type="button" variant="ghost" size="icon" className="size-7" onClick={onCancel} aria-label="Cancel upload">
            <X />
          </Button>
        )}
        {status === 'error' && onRetry && (
          <Button type="button" variant="ghost" size="icon" className="size-7" onClick={onRetry} aria-label="Retry upload">
            <RotateCcw />
          </Button>
        )}
        {status !== 'uploading' && onClose && (
          <Button type="button" variant="ghost" size="icon" className="size-7" onClick={onClose} aria-label="Close">
            <X />
          </Button>
        )}
      </div>

      <div
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.floor(percent)}
        className="mt-2.5 h-1.5 overflow-hidden rounded-full bg-foreground/10"
      >
        <div
          className={cn(
            'h-full rounded-full transition-[width] duration-200',
            status === 'error' ? 'bg-destructive' : 'bg-gradient-to-r from-emerald-400 to-sky-400',
          )}
          style={{ width: `${percent}%` }}
        />
      </div>

      {status === 'error' && <p className="mt-2 text-sm text-destructive">{error}</p>}

      {progress && (
        <dl className="mt-2.5 grid grid-cols-2 gap-x-3 gap-y-2">
          <Stat label="Uploaded" value={`${formatBytes(progress.loadedBytes)} / ${formatBytes(progress.totalBytes)}`} />
          <Stat label="Speed" value={status === 'uploading' ? `${formatBytes(progress.speed)}/s` : '—'} />
        </dl>
      )}
    </div>
  )
}
