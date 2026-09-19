import { Bot, Wrench } from 'lucide-react'
import { LiveMap } from '@/components/layout/LiveMap'

/** Static product mockup: a chat exchange next to the map it produced. */
export function MapPreview() {
  return (
    <div className="grid overflow-hidden rounded-2xl border border-border bg-card shadow-2xl shadow-emerald-500/5 md:grid-cols-[2fr_3fr] ">
      <div className="flex flex-col gap-3 border-b border-border p-4 text-sm md:border-r md:border-b-0">
        <div className="self-end rounded-xl rounded-br-sm bg-primary px-3 py-2 text-primary-foreground">
          Buffer the river by 500 m and tell me the area in km².
        </div>
        <div className="flex items-center gap-2 rounded-lg border border-border bg-muted/50 px-3 py-2 font-mono text-xs text-muted-foreground">
          <Wrench className="size-3.5 text-emerald-500" />
          buffer_geometry_tool
          <span className="ml-auto text-emerald-500">done</span>
        </div>
        <div className="flex items-center gap-2 rounded-lg border border-border bg-muted/50 px-3 py-2 font-mono text-xs text-muted-foreground">
          <Wrench className="size-3.5 text-emerald-500" />
          calculate_area_tool
          <span className="ml-auto text-emerald-500">done</span>
        </div>
        <div className="flex gap-2">
          <Bot className="mt-0.5 size-4 shrink-0 text-emerald-500" />
          <p className="text-muted-foreground">
            The 500 m buffer covers <span className="text-foreground">12.4 km²</span>. I've added it to the map as a new layer.
          </p>
        </div>
      </div>

      <LiveMap bare />
    </div>
  )
}
