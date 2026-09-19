import type { Metadata } from 'next'
import { ChatPage } from '@/features/chat/ChatPage'

export const metadata: Metadata = { title: 'GeoAgent · Chat' }

export default function Page() {
  return <ChatPage />
}
