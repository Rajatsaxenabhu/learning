import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import { Providers } from './providers'
import './globals.css'

export const metadata: Metadata = {
  title: 'GeoAgent',
  icons: { icon: '/favicon.svg' },
}

// applies the saved theme before first paint so there is no light/dark flash
const themeScript = `try{var t=localStorage.getItem('theme');document.documentElement.classList.toggle('dark',t!=='light')}catch(e){document.documentElement.classList.add('dark')}`

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
