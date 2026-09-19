'use client'

import type { ReactNode } from 'react'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import { ThemeProvider, useTheme } from '@/lib/theme'

function Toasts() {
  const { theme } = useTheme()
  return <ToastContainer theme={theme} position="top-right" />
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <Toasts />
      {children}
    </ThemeProvider>
  )
}
