import { LiveMap } from '@/components/layout/LiveMap'

/** Product mockup: the live map the agent produces. */
export function MapPreview() {
  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-card shadow-2xl shadow-emerald-500/5">
      <LiveMap bare className="!min-h-96 md:!min-h-[32rem] lg:!min-h-[36rem]" />
    </div>
  )
}
