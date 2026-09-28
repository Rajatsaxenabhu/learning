'use client'

import { useEffect, useRef, type ComponentProps, type PointerEvent } from 'react'
import { Card } from '@/components/ui/card'
import { cn } from 'cn'

/** Circle that blend-inverts whatever is under it: red in light mode, light yellow in dark mode. */
function InvertDot({ size, showOnHover = false }: { size: string; showOnHover?: boolean }) {
  return (
    <div
      aria-hidden
      className={cn(
        'pointer-events-none absolute rounded-full bg-red-500 mix-blend-difference blur-xl transition-opacity duration-200 dark:bg-yellow-200',
        showOnHover ? 'opacity-0 group-hover:opacity-100' : 'opacity-100',
        size,
      )}
      style={{
        left: 'var(--spot-x, 50%)',
        top: 'var(--spot-y, 50%)',
        transform: 'translate(-50%, -50%)',
      }}
    />
  )
}

/** Card whose pixels invert color in a circle that tracks the cursor. */
export function SpotlightCard({ className, children, ...props }: ComponentProps<typeof Card>) {
  const ref = useRef<HTMLDivElement>(null)

  function handlePointerMove(e: PointerEvent<HTMLDivElement>) {
    const rect = ref.current?.getBoundingClientRect()
    if (!rect) return
    ref.current!.style.setProperty('--spot-x', `${e.clientX - rect.left}px`)
    ref.current!.style.setProperty('--spot-y', `${e.clientY - rect.top}px`)
  }

  return (
    <Card ref={ref} onPointerMove={handlePointerMove} className={cn('group relative', className)} {...props}>
      <div className="relative z-10 flex flex-1 flex-col gap-(--card-spacing)">{children}</div>
      <InvertDot size="size-32" showOnHover />
    </Card>
  )
}

/** Same invert-circle effect, tracking the cursor across the whole page. */
export function CursorGlow() {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleMove(e: globalThis.PointerEvent) {
      const el = ref.current
      if (!el) return
      el.style.setProperty('--spot-x', `${e.clientX}px`)
      el.style.setProperty('--spot-y', `${e.clientY}px`)
    }
    window.addEventListener('pointermove', handleMove)
    return () => window.removeEventListener('pointermove', handleMove)
  }, [])

  return (
    <div ref={ref} className="pointer-events-none fixed inset-0">
      <InvertDot size="size-40" />
    </div>
  )
}
