'use client'

import { type ComponentType } from 'react'
import {
  Bot,
  ArrowRight,
  Layers,
  MessageSquare,
  Plug,
  Ruler,
  Shapes,
  Globe2,
  ShieldCheck,
  Database,
  FileImage,
  SlidersHorizontal,
  BarChart3,
  Cpu,
  Gpu,
  MemoryStick,
  Map as MapIcon,
  ExternalLink,
} from 'lucide-react'
import { Reveal } from './Reveal'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { SpotlightCard } from './Spotlight'

type Item = {
  icon: ComponentType<{ className?: string }>
  title: string
  body: string
}

const features: Item[] = [
  {
    icon: MessageSquare,
    title: 'Talk to your map',
    body: 'Describe the analysis in plain language. The agent plans the steps and runs them for you.',
  },
  {
    icon: Plug,
    title: 'Built on MCP',
    body: 'GIS operations are exposed as Model Context Protocol tools, so any MCP-compatible client can use them.',
  },
  {
    icon: Bot,
    title: 'Agentic, not scripted',
    body: 'A LangGraph agent chains tools, inspects results and recovers from errors on its own.',
  },
  {
    icon: Layers,
    title: 'Results as layers',
    body: 'Every output lands on the map as a GeoJSON layer you can inspect, toggle and download.',
  },
]

const toolGroups: Item[] = [
  {
    icon: Database,
    title: 'Vector data & query',
    body: 'Inspect layers and pull out the features you need.',
  },
  {
    icon: Shapes,
    title: 'Vector geometry',
    body: 'Combine and reshape features.',
  },
  {
    icon: Ruler,
    title: 'Measurement',
    body: 'Areas, lengths, centroids and extents.',
  },
  {
    icon: Globe2,
    title: 'Projection & CRS',
    body: 'Reproject data and pick the right coordinate system.',
  },
  {
    icon: ShieldCheck,
    title: 'Validation',
    body: 'Catch bad inputs early, before they break an analysis.',
  },
  {
    icon: FileImage,
    title: 'Raster metadata',
    body: 'Read size, bands, CRS and resolution straight from the file.',
  },
  {
    icon: SlidersHorizontal,
    title: 'Raster processing',
    body: 'Clip, warp and convert between raster and vector.',
  },
  {
    icon: BarChart3,
    title: 'Raster statistics',
    body: 'Summarize pixel values across a raster.',
  },
]

const stack = [
  { group: 'Frontend', items: ['Next.js', 'React', 'Tailwind CSS'] },
  { group: 'Agent & API', items: ['FastAPI', 'LangGraph', 'MCP'] },
  { group: 'GIS engine', items: ['GDAL', 'Shapely', 'PostGIS'] },
  { group: 'Data & retrieval', items: ['PostgreSQL', 'Redis', 'Qdrant'] },
  { group: 'Serving & infra', items: ['vLLM', 'Docker', 'Traefik'] },
]

const hardware = [
  { icon: Gpu, role: 'LLM serving', card: 'RTX 5070 Ti', body: 'Runs vLLM hosting Qwen3-4B-Thinking-2507 (FP8), plus embedding and reranking, all on a single GPU.' },
  { icon: Cpu, role: 'CPU', card: 'Intel Core i9', body: 'Handles the API, GIS processing and everything outside the GPU.' },
  { icon: MemoryStick, role: 'Memory', card: '32 GB RAM', body: 'Headroom for Postgres, Redis, Qdrant and raster processing running side by side.' },
]

const archNodes = [
  { icon: MessageSquare, title: 'Browser', body: 'You ask a question or drop a layer on the map.' },
  { icon: Layers, title: 'Next.js + FastAPI', body: 'The request streams in over the API.' },
  { icon: Bot, title: 'LangGraph agent', body: 'Plans the steps and picks the right tools.' },
  { icon: Plug, title: 'MCP tool server', body: 'Runs the vector & raster GIS operations.' },
  { icon: Gpu, title: 'vLLM · RTX 5070 Ti', body: 'Qwen3-4B-Thinking reasons over each tool result and decides what’s next.' },
  { icon: Database, title: 'Postgres · Redis · Qdrant', body: 'Persists layers and retrieves context (embedded on the same GPU).' },
  { icon: MapIcon, title: 'Live map', body: 'The result streams back as a GeoJSON layer.' },
]

const steps = [
  { n: '01', title: 'Ask', body: 'Type a question or upload a GeoJSON layer.' },
  { n: '02', title: 'Plan', body: 'The agent picks the right GIS tools and their order.' },
  { n: '03', title: 'Execute', body: 'Tools run on the MCP server; every call is streamed back live.' },
  { n: '04', title: 'See', body: 'Results are drawn on the map with a written explanation.' },
]

function Heading({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <Reveal className="mx-auto mb-8 max-w-2xl text-center">
      <Badge variant="outline" className="mb-2 font-mono tracking-widest text-emerald-500 uppercase">
        {eyebrow}
      </Badge>
      <h2 className="mt-2 text-3xl font-semibold tracking-tight text-balance md:text-4xl">{title}</h2>
    </Reveal>
  )
}

function FeatureCard({ item, delay }: { item: Item; delay: number }) {
  const { icon: Icon, title, body } = item

  return (
    <Reveal delay={delay} className="h-full">
      <Card className="h-full ring-foreground/10 transition-all duration-300 hover:-translate-y-1 hover:ring-emerald-400/50">
        <CardHeader>
          <span className="mb-2 flex size-10 items-center justify-center rounded-lg bg-emerald-500/10 ring-1 ring-emerald-500/20">
            <Icon className="size-5 text-emerald-500" />
          </span>
          <CardTitle>{title}</CardTitle>
          <CardDescription>{body}</CardDescription>
        </CardHeader>
      </Card>
    </Reveal>
  )
}

export function Features() {
  return (
    <section id="features" className="w-full scroll-mt-16 px-4 py-14 sm:px-8 lg:px-16">
      <Heading eyebrow="Features" title="Spatial analysis without the GIS learning curve" />
      <div className="grid items-start gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {features.map((f, i) => (
          <FeatureCard key={f.title} item={f} delay={i * 100} />
        ))}
      </div>
    </section>
  )
}

export function HowItWorks() {
  return (
    <section id="how-it-works" className="w-full scroll-mt-16 border-y border-border bg-muted/40 px-4 py-14 sm:px-8 lg:px-16">
      <Heading eyebrow="How it works" title="From question to map in four steps" />
      <ol className="relative grid gap-8 md:grid-cols-4">
        <div aria-hidden className="absolute top-5 right-[12.5%] left-[12.5%] hidden border-t border-dashed border-emerald-500/40 md:block" />
        {steps.map((s, i) => (
          <li key={s.n}>
            <Reveal delay={i * 150} className="flex flex-col items-center text-center">
              <span className="relative flex size-10 items-center justify-center rounded-full border border-emerald-500/50 bg-background font-mono text-sm text-emerald-500">
                {s.n}
              </span>
              <h3 className="mt-4 mb-1 text-lg font-medium">{s.title}</h3>
              <p className="max-w-56 text-sm text-muted-foreground">{s.body}</p>
            </Reveal>
          </li>
        ))}
      </ol>
    </section>
  )
}

export function Tools() {
  return (
    <section id="tools" className="w-full scroll-mt-16 px-4 py-14 sm:px-8 lg:px-16">
      <Heading eyebrow="MCP toolbox" title="Vector and raster tools the agent can call" />
      <div className="grid items-start gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {toolGroups.map((t, i) => (
          <FeatureCard key={t.title} item={t} delay={i * 100} />
        ))}
      </div>
    </section>
  )
}

export function Architecture() {
  return (
    <section id="architecture" className="w-full scroll-mt-16 px-4 py-14 sm:px-8 lg:px-16">
      <Heading eyebrow="System architecture" title="How a question becomes a map" />
      <Reveal className="mx-auto max-w-6xl">
        <div className="group overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_6%,black_94%,transparent)]">
          <div className="flex w-max gap-3 animate-marquee group-hover:[animation-play-state:paused] motion-reduce:animate-none">
            {[...archNodes, ...archNodes].map((node, i) => (
              <div key={`${node.title}-${i}`} className="flex shrink-0 items-stretch gap-3">
                <div className="flex w-56 flex-col gap-3 rounded-xl border border-border bg-card p-5 ring-1 ring-foreground/10">
                  <span className="flex size-11 items-center justify-center rounded-lg bg-emerald-500/10 ring-1 ring-emerald-500/20">
                    <node.icon className="size-5 text-emerald-500" />
                  </span>
                  <div>
                    <h3 className="font-medium">{node.title}</h3>
                    <p className="mt-1 text-sm text-muted-foreground">{node.body}</p>
                  </div>
                </div>
                <div className="flex w-6 shrink-0 items-center justify-center">
                  <ArrowRight className="size-5 text-emerald-500/60" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </Reveal>
    </section>
  )
}

export function About() {
  return (
    <section id="about" className="w-full scroll-mt-16 bg-muted/40 px-4 py-16 sm:px-8 lg:px-16">
      <Heading eyebrow="Under the hood" title="Stack, hardware and who built it" />

      <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-2">
        <Reveal>
          <SpotlightCard className="h-full ring-foreground/10 [--card-spacing:--spacing(6)]">
            <CardHeader>
              <div className="mb-3 flex items-center gap-3">
                <span className="flex size-12 items-center justify-center rounded-lg bg-emerald-500/10 ring-1 ring-emerald-500/20">
                  <Layers className="size-6 text-emerald-500" />
                </span>
                <CardTitle className="text-xl">Tech stack</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {stack.map((s) => (
                <div key={s.group} className="flex flex-col gap-2 sm:flex-row sm:gap-4">
                  <dt className="w-36 shrink-0 text-sm font-medium text-muted-foreground">{s.group}</dt>
                  <dd className="flex flex-wrap gap-2">
                    {s.items.map((i) => (
                      <Badge key={i} variant="secondary" className="h-auto px-2.5 py-1 text-sm">
                        {i}
                      </Badge>
                    ))}
                  </dd>
                </div>
              ))}
            </CardContent>
          </SpotlightCard>
        </Reveal>

        <Reveal delay={100}>
          <SpotlightCard className="h-full ring-foreground/10 [--card-spacing:--spacing(6)]">
            <CardHeader>
              <div className="mb-3 flex items-center gap-3">
                <span className="flex size-12 items-center justify-center rounded-lg bg-emerald-500/10 ring-1 ring-emerald-500/20">
                  <Cpu className="size-6 text-emerald-500" />
                </span>
                <CardTitle className="text-xl">Hardware</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-5">
              {hardware.map((h) => (
                <div key={h.card} className="flex items-start gap-4">
                  <span className="mt-0.5 flex size-10 shrink-0 items-center justify-center rounded-md bg-emerald-500/10 ring-1 ring-emerald-500/20">
                    <h.icon className="size-5 text-emerald-500" />
                  </span>
                  <div>
                    <p className="flex flex-wrap items-center gap-2 text-base font-medium">
                      {h.card}
                      <Badge variant="outline">{h.role}</Badge>
                    </p>
                    <p className="mt-0.5 text-sm text-muted-foreground">{h.body}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </SpotlightCard>
        </Reveal>

        <Reveal delay={200} className="lg:col-span-2">
          <SpotlightCard className="ring-foreground/10 [--card-spacing:--spacing(6)]">
            <CardContent className="flex flex-wrap items-center justify-between gap-6">
              <div className="flex items-center gap-5">
                <span className="flex size-16 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-sky-500 font-mono text-lg font-semibold text-white">
                  RS
                </span>
                <div>
                  <CardTitle className="text-xl">Built by Rajat Saxena</CardTitle>
                  <CardDescription className="mt-1 text-base">
                    Designed and built GeoAgent end to end — the agent, the MCP toolbox and the self-hosted inference stack.
                  </CardDescription>
                </div>
              </div>
              <Button
                size="lg"
                variant="outline"
                nativeButton={false}
                render={<a href="https://www.linkedin.com/in/rajat-saxena-7061271a3/" target="_blank" rel="noopener noreferrer" />}
              >
                Connect on LinkedIn <ExternalLink />
              </Button>
            </CardContent>
          </SpotlightCard>
        </Reveal>
      </div>
    </section>
  )
}
