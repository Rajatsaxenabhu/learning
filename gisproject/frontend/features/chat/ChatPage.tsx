'use client'

import { useState } from 'react'
import { toast } from 'react-toastify'
import { useChunkedUpload } from '@/hooks/useChunkedUpload'
import { cn } from '@/lib/utils'
import { useSessionStore } from '@/store/session'
import { ChatComposer } from './ChatComposer'
import { ChatHeader } from './ChatHeader'
import { MessageList } from './MessageList'
import { StatusScreen } from './StatusScreen'
import { gradientBg } from './constants'
import { useChatSocket } from './useChatSocket'
import { useReadySession } from './useReadySession'

function wsUrlFor(sessionId: string): string {
  return `${process.env.NEXT_PUBLIC_WS_URL}/api/ws/start/${sessionId}`
}

export function ChatPage() {
  const { status, message, retry } = useReadySession()
  const sessionId = useSessionStore((s) => s.sessionId)
  const chat = useChatSocket(status === 'ready' && sessionId ? wsUrlFor(sessionId) : '')
  const upload = useChunkedUpload()
  const [input, setInput] = useState('')
  // set once an upload finishes; attached to the next message so the agent knows which file to use
  const [attachedId, setAttachedId] = useState<string | null>(null)

  async function pickFile(file: File) {
    setAttachedId(null)
    const result = await upload.start(file)
    if (result) {
      setAttachedId(result.dataset_id)
      toast.success(`${file.name} uploaded`)
    }
  }

  function submit() {
    const q = input.trim()
    if (!q || upload.state.status === 'uploading') return
    const attached = upload.state.status === 'done' && attachedId ? upload.state : null
    if (chat.send(q, q, attached?.result.dataset_id)) {
      setInput('')
      setAttachedId(null)
      if (attached) upload.reset()
    }
  }

  if (status !== 'ready') return <StatusScreen status={status} message={message} onRetry={retry} />

  return (
    <div className={cn('flex h-svh flex-col text-foreground', gradientBg)}>
      <ChatHeader isConnected={chat.isConnected} />
      <MessageList
        messages={chat.messages}
        loading={chat.loading}
        streaming={chat.streaming}
        approval={chat.approval}
        onAnswerApproval={chat.answerApproval}
        onPickPrompt={setInput}
      />
      <ChatComposer
        input={input}
        onInputChange={setInput}
        onSubmit={submit}
        loading={chat.loading || upload.state.status === 'uploading'}
        totalTokens={chat.totalTokens}
        upload={upload.state}
        onPickFile={pickFile}
        onCancelUpload={upload.cancel}
        onClearUpload={() => {
          upload.reset()
          setAttachedId(null)
        }}
      />
    </div>
  )
}
