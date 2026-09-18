import { Bot, Wrench } from 'lucide-react'

/** Static product mockup: a chat exchange next to the map it produced. */
export function MapPreview() {
  return (
    <div className="grid overflow-hidden rounded-2xl border border-border bg-card shadow-2xl shadow-emerald-500/5 md:grid-cols-[2fr_3fr]">
      <div className="flex flex-col gap-3 border-b border-border p-4 text-sm md:border-r md:border-b-0">
        <div className="self-end rounded-xl rounded-br-sm bg-primary px-3 py-2 text-primary-foreground">
          Buffer the river by 500 m and tell me the area in km².
        </div>
        <div className="flex items-center gap-2 rounded-lg border border-border bg-muted/50 px-3 py-2 font-mono text-xs text-muted-foreground">
          <Wrench className="size-3.5 text-emerald-400" />
          buffer_geometry_tool
          <span className="ml-auto text-emerald-400">done</span>
        </div>
        <div className="flex items-center gap-2 rounded-lg border border-border bg-muted/50 px-3 py-2 font-mono text-xs text-muted-foreground">
          <Wrench className="size-3.5 text-emerald-400" />
          calculate_area_tool
          <span className="ml-auto text-emerald-400">done</span>
        </div>
        <div className="flex gap-2">
          <Bot className="mt-0.5 size-4 shrink-0 text-emerald-400" />
          <p className="text-muted-foreground">
            The 500 m buffer covers <span className="text-foreground">12.4 km²</span>. I've added it to the map as a new layer.
          </p>
        </div>
      </div>

      <div className="relative min-h-64 bg-[#0b1512]">
        <svg viewBox="0 0 300 220" className="absolute inset-0 size-full" preserveAspectRatio="xMidYMid slice" aria-hidden>
          <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M20 0H0V20" fill="none" stroke="currentColor" strokeWidth="0.4" className="text-emerald-900/60" />
            </pattern>
          </defs>
          <rect width="300" height="220" fill="url(#grid)" />
          <path
            d="M-10 60 C50 90 80 30 140 80 S230 150 310 110"
            fill="none"
            stroke="#38bdf8"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <path
            d="M-10 60 C50 90 80 30 140 80 S230 150 310 110"
            fill="none"
            stroke="#10b981"
            strokeOpacity="0.25"
            strokeWidth="38"
            strokeLinecap="round"
          />
          <circle cx="140" cy="80" r="4" fill="#facc15" />
          <circle cx="220" cy="140" r="4" fill="#facc15" />
          <circle cx="70" cy="70" r="4" fill="#facc15" />
        </svg>
        <span className="absolute top-3 left-3 rounded-md bg-background/80 px-2 py-1 font-mono text-xs text-muted-foreground backdrop-blur">
          EPSG:4326 · 2 layers
        </span>
      </div>
    </div>
  )
}
