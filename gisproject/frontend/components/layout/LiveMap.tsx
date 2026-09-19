'use client'

import { useEffect, useState } from 'react'

const RIVER = 'M-10 120 C50 150 80 70 140 120 S230 190 310 140'
const POINTS: [number, number, string][] = [
  [70, 118, '0s'],
  [140, 120, '0.7s'],
  [220, 158, '1.4s'],
]

/** Decorative animated map: flowing river, pulsing buffer, pinging points and a live cursor readout. */
export function LiveMap({ className, bare }: { className?: string; bare?: boolean }) {
  const [pos, setPos] = useState({ lat: 28.6139, lng: 77.209 })

  useEffect(() => {
    const id = setInterval(
      () => setPos((p) => ({ lat: p.lat + (Math.random() - 0.5) * 0.004, lng: p.lng + (Math.random() - 0.5) * 0.004 })),
      900,
    )
    return () => clearInterval(id)
  }, [])

  return (
    <div
      className={`relative overflow-hidden bg-[#0b1512] ${bare ? 'h-full min-h-72' : 'rounded-3xl border border-border/60 shadow-lg'} ${className ?? ''}`}
    >
      <svg viewBox="0 0 300 200" className={bare ? 'absolute inset-0 size-full' : 'block h-44 w-full'} preserveAspectRatio="xMidYMid slice" aria-hidden>
        <defs>
          <pattern id="live-grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M20 0H0V20" fill="none" stroke="#065f46" strokeOpacity="0.55" strokeWidth="0.5" />
            <animateTransform attributeName="patternTransform" type="translate" from="0 0" to="20 20" dur="6s" repeatCount="indefinite" />
          </pattern>
          <linearGradient id="live-sweep" x1="0" x2="1">
            <stop offset="0" stopColor="#34d399" stopOpacity="0" />
            <stop offset="1" stopColor="#34d399" stopOpacity="0.35" />
          </linearGradient>
        </defs>
        <rect width="300" height="200" fill="url(#live-grid)" />

        <path d={RIVER} fill="none" stroke="#10b981" strokeWidth="34" strokeLinecap="round" strokeOpacity="0.2">
          <animate attributeName="stroke-opacity" values="0.12;0.28;0.12" dur="3s" repeatCount="indefinite" />
        </path>
        <path d={RIVER} fill="none" stroke="#38bdf8" strokeWidth="3" strokeLinecap="round" />
        <path d={RIVER} fill="none" stroke="#e0f2fe" strokeWidth="1.2" strokeLinecap="round" strokeDasharray="6 14">
          <animate attributeName="stroke-dashoffset" from="20" to="0" dur="1.2s" repeatCount="indefinite" />
        </path>

        {POINTS.map(([x, y, begin]) => (
          <g key={x}>
            <circle cx={x} cy={y} r="4" fill="#facc15" />
            <circle cx={x} cy={y} r="4" fill="none" stroke="#facc15" strokeWidth="1.5">
              <animate attributeName="r" values="4;16" dur="2s" begin={begin} repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.8;0" dur="2s" begin={begin} repeatCount="indefinite" />
            </circle>
          </g>
        ))}

        <rect x="-60" y="0" width="60" height="200" fill="url(#live-sweep)">
          <animate attributeName="x" from="-60" to="300" dur="4s" repeatCount="indefinite" />
        </rect>
      </svg>

      <span className="absolute top-3 left-3 flex items-center gap-1.5 rounded-full bg-black/40 px-2.5 py-1 font-mono text-[10px] text-emerald-300 backdrop-blur">
        <span className="size-1.5 animate-pulse rounded-full bg-emerald-400" /> LIVE
      </span>
      <span className="absolute right-3 bottom-3 rounded-full bg-black/40 px-2.5 py-1 font-mono text-[10px] text-slate-300 tabular-nums backdrop-blur">
        {pos.lat.toFixed(4)}°N {pos.lng.toFixed(4)}°E · EPSG:4326
      </span>
    </div>
  )
}
