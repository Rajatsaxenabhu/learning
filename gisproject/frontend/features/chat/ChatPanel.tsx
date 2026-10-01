'use client'

import { useState } from 'react'
import { toast } from 'react-toastify'
import { useChunkedUpload } from '@/hooks/useChunkedUpload'
import { ChatComposer } from './ChatComposer'
import { MessageList } from './MessageList'
import type { useChatSocket } from './useChatSocket'

/** Transcript + composer. The socket is owned by the parent so the navbar can show its connection state. */
export function ChatPanel({ chat }: { chat: ReturnType<typeof useChatSocket> }) {
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

  return (
    <>
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
    </>
  )
}
