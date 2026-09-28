import { Compass } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/layout/ThemeToggle'

const links = [
  { href: '/', label: 'Home' },
  { href: '/#features', label: 'Features' },
  { href: '/#tools', label: 'Tools' },
  { href: '/about', label: 'About' },
]

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-background/70 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-8 lg:px-16">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <Compass className="size-5 text-emerald-500" />
          GeoAgent
        </Link>
        <nav className="hidden items-center gap-6 text-sm text-muted-foreground md:flex">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="transition-colors hover:text-foreground">
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button size="sm" nativeButton={false} render={<Link href="/chat" />}>
            Launch app
          </Button>
        </div>
      </div>
    </header>
  )
}
