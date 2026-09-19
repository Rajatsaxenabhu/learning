import { useState, type ComponentType } from 'react'
import { Bot, ChevronDown, Layers, MessageSquare, Plug, Ruler, Shapes, Globe2, ShieldCheck } from 'lucide-react'
import { cn } from 'cn'
import { Reveal } from './Reveal'

type Item = {
  icon: ComponentType<{ className?: string }>
  title: string
  body: string
  detail: string
}

const features: Item[] = [
  {
    icon: MessageSquare,
    title: 'Talk to your map',
    body: 'Describe the analysis in plain language. The agent plans the steps and runs them for you.',
    detail: 'Try "which parcels fall inside the flood zone?" — the agent works out the projection, the overlay and the area calculation itself.',
  },
  {
    icon: Plug,
    title: 'Built on MCP',
    body: 'GIS operations are exposed as Model Context Protocol tools, so any MCP-compatible client can use them.',
    detail: 'The server speaks both stdio and HTTP, so the same toolbox works from this app, Claude Desktop or your own scripts.',
  },
  {
    icon: Bot,
    title: 'Agentic, not scripted',
    body: 'A LangGraph agent chains tools, inspects results and recovers from errors on its own.',
    detail: 'If a geometry is invalid or in the wrong CRS, the agent validates or reprojects it and retries instead of failing.',
  },
  {
    icon: Layers,
    title: 'Results as layers',
    body: 'Every output lands on the map as a GeoJSON layer you can inspect, toggle and download.',
    detail: 'Layers are kept per conversation, so you can build on earlier results ("now intersect that with the roads layer").',
  },
]

const toolGroups: Item[] = [
  {
    icon: Globe2,
    title: 'Projection',
    body: 'Reproject data and pick the right coordinate system.',
    detail: 'transform_geometry · get_crs_info · is_projected_crs · calculate_utm_zone',
  },
  {
    icon: Ruler,
    title: 'Measurement',
    body: 'Areas, lengths, centroids and extents.',
    detail: 'calculate_area · calculate_length · calculate_centroid · bounds',
  },
  {
    icon: Shapes,
    title: 'Geometry',
    body: 'Combine and reshape features.',
    detail: 'buffer · intersection · difference · union · simplify · convex_hull',
  },
  {
    icon: ShieldCheck,
    title: 'Validation',
    body: 'Catch bad inputs early.',
    detail: 'validate_geometry reports why a geometry is invalid before it breaks an analysis.',
  },
]

const steps = [
  { n: '01', title: 'Ask', body: 'Type a question or upload a GeoJSON layer.' },
  { n: '02', title: 'Plan', body: 'The agent picks the right GIS tools and their order.' },
  { n: '03', title: 'Execute', body: 'Tools run on the MCP server; every call is streamed back live.' },
  { n: '04', title: 'See', body: 'Results are drawn on the map with a written explanation.' },
]

function Heading({ eyebrow, title }: { eyebrow: string; title: string }) {
  return (
    <Reveal className="mx-auto mb-12 max-w-2xl text-center">
      <p className="mb-2 font-mono text-xs tracking-widest text-emerald-500 uppercase">{eyebrow}</p>
      <h2 className="text-3xl font-semibold tracking-tight text-balance md:text-4xl">{title}</h2>
    </Reveal>
  )
}

/** Card that expands on click to reveal more detail. */
function ExpandCard({ item, delay }: { item: Item; delay: number }) {
  const [open, setOpen] = useState(false)
  const { icon: Icon, title, body, detail } = item

  return (
    <Reveal delay={delay} className="h-full">
      <button
        type="button"
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className={cn(
          'group h-full w-full cursor-pointer rounded-xl border bg-card p-6 text-left transition-all duration-300 hover:-translate-y-1 hover:border-emerald-400/50',
          open ? 'border-emerald-400/60 shadow-lg shadow-emerald-500/10' : 'border-border',
        )}
      >
        <div className="mb-4 flex items-center justify-between">
          <span className="flex size-10 items-center justify-center rounded-lg bg-emerald-500/10 ring-1 ring-emerald-500/20">
            <Icon
              className={cn(
                'size-5 text-emerald-500 transition-transform duration-300',
                open ? 'scale-125 rotate-6' : 'group-hover:scale-110',
              )}
            />
          </span>
          <ChevronDown
            className={cn('size-4 text-muted-foreground transition-transform duration-300', open && 'rotate-180')}
          />
        </div>
        <h3 className="mb-1 font-medium">{title}</h3>
        <p className="text-sm text-muted-foreground">{body}</p>
        <div
          className={cn(
            'grid transition-all duration-300 ease-out',
            open ? 'mt-3 grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0',
          )}
        >
          <p className="overflow-hidden border-l-2 border-emerald-400/60 pl-3 text-sm text-foreground/80">{detail}</p>
        </div>
      </button>
    </Reveal>
  )
}

export function Features() {
  return (
    <section id="features" className="w-full scroll-mt-16 px-4 py-20 sm:px-8 lg:px-16">
      <Heading eyebrow="Features" title="Spatial analysis without the GIS learning curve" />
      <div className="grid items-start gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {features.map((f, i) => (
          <ExpandCard key={f.title} item={f} delay={i * 100} />
        ))}
      </div>
    </section>
  )
}

export function HowItWorks() {
  return (
    <section id="how-it-works" className="w-full scroll-mt-16 border-y border-border bg-muted/40 px-4 py-20 sm:px-8 lg:px-16">
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
    <section id="tools" className="w-full scroll-mt-16 px-4 py-20 sm:px-8 lg:px-16">
      <Heading eyebrow="MCP toolbox" title="A growing set of GIS tools the agent can call" />
      <div className="grid items-start gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {toolGroups.map((t, i) => (
          <ExpandCard key={t.title} item={t} delay={i * 100} />
        ))}
      </div>
    </section>
  )
}
