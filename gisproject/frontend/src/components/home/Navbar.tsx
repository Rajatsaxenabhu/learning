import { Compass } from 'lucide-react'
import { Link } from 'react-router'
import { Button } from '@/components/ui/button'

const links = [
  { href: '#features', label: 'Features' },
  { href: '#how-it-works', label: 'How it works' },
  { href: '#tools', label: 'Tools' },
]

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-background/70 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <Compass className="size-5 text-emerald-400" />
          GeoAgent
        </Link>
        <nav className="hidden items-center gap-6 text-sm text-muted-foreground md:flex">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="transition-colors hover:text-foreground">
              {l.label}
            </a>
          ))}
        </nav>
        <Button size="sm" render={<Link to="/app" />}>
          Launch app
        </Button>
      </div>
    </header>
  )
}
