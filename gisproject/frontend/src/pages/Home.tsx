import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router'
import { Reveal } from '@/components/home/Reveal'
import { Button } from '@/components/ui/button'
import { Navbar } from '@/components/home/Navbar'
import { MapPreview } from '@/components/home/MapPreview'
import { Features, HowItWorks, Tools } from '@/components/home/Sections'

export default function Home() {
  return (
    <div className="min-h-svh bg-background text-foreground">
      <Navbar />

      <main>
        <section className="relative overflow-hidden border-b border-border">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,var(--border)_1px,transparent_1px),linear-gradient(to_bottom,var(--border)_1px,transparent_1px)] bg-[size:48px_48px] opacity-40 [mask-image:radial-gradient(ellipse_at_center,black,transparent_75%)]"
          />
          <div
            aria-hidden
            className="pointer-events-none absolute -top-40 left-1/4 size-[36rem] rounded-full bg-emerald-500/20 blur-3xl"
          />
          <div className="relative grid w-full items-center gap-12 px-4 py-16 sm:px-8 lg:grid-cols-[5fr_6fr] lg:gap-16 lg:px-16 lg:py-24">
            <div className="text-center lg:text-left">
              <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-background/60 px-3 py-1 font-mono text-xs text-muted-foreground backdrop-blur">
                <span className="size-1.5 rounded-full bg-emerald-500" />
                MCP + agentic AI for GIS
              </span>
              <h1 className="text-4xl font-semibold tracking-tight text-balance md:text-6xl xl:text-7xl">
                Ask questions.{' '}
                <span className="bg-gradient-to-r from-emerald-500 to-sky-500 bg-clip-text text-transparent">
                  Get maps.
                </span>
              </h1>
              <p className="mx-auto mt-6 max-w-xl text-lg text-balance text-muted-foreground lg:mx-0">
                GeoAgent is an AI analyst that runs real GIS operations for you. Describe what you need, and it plans, executes and maps the result.
              </p>
              <div className="mt-8 flex flex-wrap justify-center gap-3 lg:justify-start">
                <Button size="lg" className="h-11 px-6 text-base" render={<Link to="/app" />}>
                  Get started <ArrowRight />
                </Button>
                <Button size="lg" variant="outline" className="h-11 px-6 text-base" render={<a href="#how-it-works" />}>
                  See how it works
                </Button>
              </div>
              <dl className="mt-10 flex justify-center gap-8 lg:justify-start">
                {[
                  ['15+', 'GIS tools'],
                  ['MCP', 'open protocol'],
                  ['Live', 'streamed steps'],
                ].map(([v, l]) => (
                  <div key={l}>
                    <dt className="text-2xl font-semibold">{v}</dt>
                    <dd className="text-xs text-muted-foreground">{l}</dd>
                  </div>
                ))}
              </dl>
            </div>
            <div className="relative">
              <MapPreview />
            </div>
          </div>
        </section>

        <Features />
        <HowItWorks />
        <Tools />

        <section className="w-full px-4 py-20 sm:px-8 lg:px-16">
          <Reveal className="rounded-3xl border border-border bg-gradient-to-br from-emerald-500/15 via-card to-sky-500/10 px-6 py-20 text-center">
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
