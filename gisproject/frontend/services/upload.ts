import { api } from '@/services/api'

export type UploadResult = {
  dataset_id: string
}

export type UploadProgress = {
  loadedBytes: number
  totalBytes: number
  percent: number
  chunksDone: number
  totalChunks: number
  /** bytes per second, averaged over the last few seconds */
  speed: number
  etaSeconds: number | null
}

export type UploadOptions = {
  chunkSize?: number
  concurrency?: number
  retries?: number
  signal?: AbortSignal
  onProgress?: (p: UploadProgress) => void
}

export const MAX_UPLOAD_BYTES = 500 * 1024 * 1024

const SPEED_WINDOW_MS = 3000

function newUploadId(): string {
  return crypto.randomUUID().replaceAll('-', '')
}

const sleep = (ms: number, signal?: AbortSignal) =>
  new Promise<void>((resolve, reject) => {
    const t = setTimeout(resolve, ms)
    signal?.addEventListener('abort', () => (clearTimeout(t), reject(signal.reason)), { once: true })
  })

export function validateFile(file: File): string | null {
  if (file.size === 0) return 'File is empty'
  if (file.size > MAX_UPLOAD_BYTES) return 'File exceeds the 500 MB limit'
  return null
}

/**
 * Splits a file into chunks, uploads them in parallel to /api/upload_data_chunk,
 * then asks the backend to merge them via /api/upload/complete.
 */
export async function uploadFileInChunks(file: File, opts: UploadOptions = {}): Promise<UploadResult> {
  const { chunkSize = 5 * 1024 * 1024, concurrency = 3, retries = 3, signal, onProgress } = opts
  const uploadId = newUploadId()
  const totalChunks = Math.max(1, Math.ceil(file.size / chunkSize))
  const loadedPerChunk = new Array<number>(totalChunks).fill(0)
  const samples: { t: number; bytes: number }[] = []
  let chunksDone = 0

  const report = () => {
    const loadedBytes = Math.min(
      file.size,
      loadedPerChunk.reduce((a, b) => a + b, 0),
    )
    const now = performance.now()
    samples.push({ t: now, bytes: loadedBytes })
    while (samples.length > 2 && now - samples[0].t > SPEED_WINDOW_MS) samples.shift()
    const first = samples[0]
    const elapsed = (now - first.t) / 1000
    const speed = elapsed > 0 ? (loadedBytes - first.bytes) / elapsed : 0
    onProgress?.({
      loadedBytes,
      totalBytes: file.size,
      percent: (loadedBytes / file.size) * 100,
      chunksDone,
      totalChunks,
      speed,
      etaSeconds: speed > 0 ? (file.size - loadedBytes) / speed : null,
    })
  }

  async function sendChunk(index: number) {
    const start = index * chunkSize
    const blob = file.slice(start, Math.min(start + chunkSize, file.size))
    for (let attempt = 0; ; attempt++) {
      const form = new FormData()
      form.append('file', blob, `${index}.part`)
      try {
        await api.post('/api/upload_data_chunk', {
          body: form,
          headers: { 'upload-id': uploadId, 'chunk-index': String(index) },
          signal,
          onUploadProgress: (e) => {
            loadedPerChunk[index] = Math.min(e.loaded, blob.size)
            report()
          },
        })
        loadedPerChunk[index] = blob.size
        chunksDone++
        report()
        return
      } catch (e) {
        loadedPerChunk[index] = 0
        // 4xx (e.g. 413 too large) will not succeed on retry, and the backend has already dropped the upload
        const status = (e as { status?: number }).status
        if (signal?.aborted || (status && status < 500) || attempt >= retries) throw e
        await sleep(500 * 2 ** attempt, signal)
      }
    }
  }

  report()
  let next = 0
  const worker = async () => {
    while (next < totalChunks) await sendChunk(next++)
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, totalChunks) }, worker))

  const { message } = await api.post<UploadResult>('/api/upload/complete', {
    body: { upload_id: uploadId, filename: file.name, total_chunks: totalChunks },
    signal,
  })
  if (!message) throw new Error('Upload could not be completed')
  return message
}
