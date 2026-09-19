import { useCallback, useRef, useState } from 'react'
import { uploadFileInChunks, validateFile, type UploadOptions, type UploadProgress, type UploadResult } from '@/services/upload'

export type UploadState =
  | { status: 'idle' }
  | { status: 'uploading'; file: File; progress: UploadProgress }
  | { status: 'done'; file: File; progress: UploadProgress; result: UploadResult }
  | { status: 'error'; file: File; progress: UploadProgress | null; error: string }

export function useChunkedUpload(options?: Omit<UploadOptions, 'signal' | 'onProgress'>) {
  const [state, setState] = useState<UploadState>({ status: 'idle' })
  const controller = useRef<AbortController | null>(null)
  const lastProgress = useRef<UploadProgress | null>(null)

  const start = useCallback(
    async (file: File): Promise<UploadResult | null> => {
      const invalid = validateFile(file)
      if (invalid) {
        setState({ status: 'error', file, progress: null, error: invalid })
        return null
      }
      controller.current?.abort()
      const ctrl = new AbortController()
      controller.current = ctrl
      lastProgress.current = null
      try {
        const result = await uploadFileInChunks(file, {
          ...options,
          signal: ctrl.signal,
          onProgress: (progress) => {
            lastProgress.current = progress
            setState({ status: 'uploading', file, progress })
          },
        })
        const last = lastProgress.current as UploadProgress | null
        const progress: UploadProgress = {
          speed: 0,
          chunksDone: last?.totalChunks ?? 1,
          totalChunks: last?.totalChunks ?? 1,
          totalBytes: file.size,
          loadedBytes: file.size,
          percent: 100,
          etaSeconds: 0,
        }
        setState({ status: 'done', file, progress, result })
        return result
      } catch (e) {
        if (ctrl.signal.aborted) setState({ status: 'idle' })
        else setState({ status: 'error', file, progress: lastProgress.current, error: e instanceof Error ? e.message : 'Upload failed' })
        return null
      }
    },
    [options],
  )

  const cancel = useCallback(() => controller.current?.abort(), [])
  const reset = useCallback(() => {
    controller.current?.abort()
    setState({ status: 'idle' })
  }, [])

  return { state, start, cancel, reset }
}
