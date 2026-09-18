import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router'
import { Reveal } from '@/components/home/Reveal'
import { Button } from '@/components/ui/button'
import { Navbar } from '@/components/home/Navbar'
import { MapPreview } from '@/components/home/MapPreview'
import { Features, HowItWorks, Tools } from '@/components/home/Sections'

export default function Home() {
  return (
    <div className="dark min-h-svh bg-background text-foreground">
      <Navbar />

      <main>
        <section className="relative overflow-hidden">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-x-0 -top-40 h-96 bg-[radial-gradient(ellipse_at_center,oklch(0.7_0.15_165/0.18),transparent_70%)]"
          />
          <div className="relative mx-auto max-w-6xl px-4 pt-20 pb-16 text-center md:pt-28">
            <span className="mb-6 inline-block rounded-full border border-border px-3 py-1 font-mono text-xs text-muted-foreground">
              MCP + agentic AI for GIS
            </span>
            <h1 className="mx-auto max-w-3xl text-4xl font-semibold tracking-tight text-balance md:text-6xl">
              Ask questions. Get maps.
            </h1>
            <p className="mx-auto mt-5 max-w-xl text-lg text-balance text-muted-foreground">
              GeoAgent is an AI analyst that runs real GIS operations for you. Describe what you need, and it plans, executes and maps the result.
            </p>
            <div className="mt-8 flex justify-center gap-3">
              <Button size="lg" render={<Link to="/app" />}>
                Get started <ArrowRight />
              </Button>
              <Button size="lg" variant="outline" render={<a href="#how-it-works" />}>
                See how it works
              </Button>
            </div>
          </div>
          <div className="relative mx-auto max-w-5xl px-4 pb-8">
            <MapPreview />
          </div>
        </section>

        <Features />
        <HowItWorks />
        <Tools />

        <section className="mx-auto max-w-6xl px-4 py-20">
          <Reveal className="rounded-2xl border border-border bg-card px-6 py-14 text-center">
            <h2 className="text-3xl font-semibold tracking-tight">Start your first analysis</h2>
            <p className="mx-auto mt-3 max-w-md text-muted-foreground">
              Upload a layer, ask a question, and watch the agent work.
            </p>
            <Button size="lg" className="mt-6" render={<Link to="/app" />}>
              Launch app <ArrowRight />
            </Button>
          </Reveal>
        </section>
      </main>

      <footer className="border-t border-border py-8 text-center text-sm text-muted-foreground">
        GeoAgent · Built with MCP, LangGraph and FastAPI
      </footer>
    </div>
  )
}
