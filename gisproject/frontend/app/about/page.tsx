import type { Metadata } from 'next'
import { Navbar } from '@/components/home/Navbar'
import { Reveal } from '@/components/home/Reveal'
import { CursorGlow } from '@/components/home/Spotlight'
import { Badge } from '@/components/ui/badge'
import { About, Architecture } from '@/components/home/Sections'

export const metadata: Metadata = { title: 'GeoAgent · About' }

export default function AboutPage() {
  return (
    <div className="min-h-svh bg-background text-foreground">
      <CursorGlow />
      <Navbar />

      <main>
        <section className="relative overflow-hidden border-b border-border">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,var(--border)_1px,transparent_1px),linear-gradient(to_bottom,var(--border)_1px,transparent_1px)] bg-[size:48px_48px] opacity-40 [mask-image:radial-gradient(ellipse_at_center,black,transparent_75%)]"
          />
          <div
            aria-hidden
            className="pointer-events-none absolute -top-40 left-1/2 size-[36rem] -translate-x-1/2 rounded-full bg-emerald-500/20 blur-3xl"
          />
          <Reveal className="relative mx-auto max-w-2xl px-4 py-12 text-center sm:px-8 lg:py-16">
            <Badge variant="outline" className="mb-6 font-mono tracking-widest text-emerald-500 uppercase">
              About
            </Badge>
            <h1 className="text-3xl font-semibold tracking-tight text-balance md:text-5xl">
              The stack, the hardware and the person behind GeoAgent
            </h1>
            <p className="mx-auto mt-4 max-w-xl text-muted-foreground">
              GeoAgent is a self-hosted GIS agent — an open protocol toolbox, a LangGraph brain, and hardware to run
              it all on.
            </p>
          </Reveal>
        </section>

        <Architecture />
        <About />
      </main>

      <footer className="border-t border-border py-8 text-center text-sm text-muted-foreground">
        GeoAgent · Built with MCP, LangGraph and FastAPI
      </footer>
    </div>
  )
}
