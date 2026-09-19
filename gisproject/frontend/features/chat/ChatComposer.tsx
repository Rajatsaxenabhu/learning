import { FileCheck2, Paperclip, SendHorizontal, X } from 'lucide-react'
import { useLayoutEffect, useRef, type FormEvent, type KeyboardEvent } from 'react'
import { UploadStats } from '@/components/upload/UploadStats'
import { Button } from '@/components/ui/button'
import type { UploadState } from '@/hooks/useChunkedUpload'

type Props = {
  input: string
  onInputChange: (value: string) => void
  onSubmit: () => void
  loading: boolean
  totalTokens: number
  upload: UploadState
  onPickFile: (file: File) => void
  onCancelUpload: () => void
  onClearUpload: () => void
}

export function ChatComposer({
  input,
  onInputChange,
  onSubmit,
  loading,
  totalTokens,
  upload,
  onPickFile,
  onCancelUpload,
  onClearUpload,
}: Props) {
  const fileInput = useRef<HTMLInputElement>(null)
  const textarea = useRef<HTMLTextAreaElement>(null)
  const uploading = upload.status === 'uploading'

  useLayoutEffect(() => {
    const el = textarea.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }, [input])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    onSubmit()
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== 'Enter' || e.shiftKey || e.nativeEvent.isComposing) return
    e.preventDefault()
    if (!loading && input.trim()) onSubmit()
  }

  return (
    <form onSubmit={handleSubmit} className="px-4 pb-4">
      {upload.status !== 'idle' && upload.status !== 'done' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/40 p-4 backdrop-blur-sm">
          <UploadStats
            className="w-full max-w-sm"
            fileName={upload.file.name}
            status={upload.status}
            progress={upload.progress}
            error={upload.status === 'error' ? upload.error : undefined}
            onCancel={onCancelUpload}
            onRetry={() => onPickFile(upload.file)}
            onClose={onClearUpload}
          />
        </div>
      )}

      {upload.status === 'done' && (
        <div className="mx-auto mb-2 flex max-w-3xl">
          <span className="inline-flex max-w-full items-center gap-2 rounded-full bg-foreground/[0.06] py-1 pl-3 pr-1 text-sm ring-1 ring-foreground/10">
            <FileCheck2 className="size-4 shrink-0 text-emerald-500" />
            <span className="truncate">{upload.file.name}</span>
            <button
              type="button"
              onClick={onClearUpload}
              className="rounded-full p-1 text-muted-foreground hover:bg-foreground/10 hover:text-foreground"
              aria-label="Remove attached file"
            >
              <X className="size-3.5" />
            </button>
          </span>
        </div>
      )}

      <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-[1.75rem] bg-foreground/[0.06] p-2 pl-3 ring-1 ring-foreground/10 transition focus-within:bg-foreground/[0.08] focus-within:ring-emerald-400/50">
        <input
          ref={fileInput}
          type="file"
          hidden
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) onPickFile(file)
            e.target.value = ''
          }}
        />
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="size-10 rounded-full"
          disabled={uploading}
          onClick={() => fileInput.current?.click()}
          aria-label="Upload a raster or vector file"
        >
          <Paperclip />
        </Button>
        <textarea
          ref={textarea}
          rows={1}
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about a layer, raster or coordinate…"
          className="max-h-[200px] min-h-12 flex-1 resize-none bg-transparent py-3 text-[15px] leading-6 outline-none placeholder:text-muted-foreground/70"
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
  )
}
