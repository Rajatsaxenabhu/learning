'use client'

import { useEffect, useState } from 'react'

const STEPS = ['Locating satellites', 'Loading map layers', 'Warming up the model']

const POINTS: [number, number, string][] = [
  [78, 92, '0s'],
  [118, 78, '0.8s'],
  [104, 124, '1.6s'],
]

export function GeoLoader({ steps = STEPS }: { steps?: string[] }) {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const id = setInterval(() => setStep((s) => (s + 1) % steps.length), 1600)
    return () => clearInterval(id)
  }, [steps.length])

  return (
    <div role="status" aria-live="polite" className="flex flex-col items-center gap-6">
      <svg viewBox="0 0 200 200" className="size-52 sm:size-60" aria-hidden>
        <defs>
          <radialGradient id="gl-globe" cx="40%" cy="35%" r="75%">
            <stop offset="0" stopColor="#34d399" stopOpacity="0.35" />
            <stop offset="1" stopColor="#0ea5e9" stopOpacity="0.08" />
          </radialGradient>
          <linearGradient id="gl-sweep" x1="0" x2="1">
            <stop offset="0" stopColor="#34d399" stopOpacity="0" />
            <stop offset="1" stopColor="#34d399" stopOpacity="0.55" />
          </linearGradient>
          <clipPath id="gl-clip">
            <circle cx="100" cy="100" r="62" />
          </clipPath>
        </defs>

        <circle cx="100" cy="100" r="62" fill="url(#gl-globe)" stroke="#34d399" strokeOpacity="0.6" strokeWidth="1.2" />

        <g clipPath="url(#gl-clip)" fill="none" stroke="#38bdf8" strokeOpacity="0.45" strokeWidth="0.7">
          <ellipse cx="100" cy="100" rx="62" ry="22" />
          <ellipse cx="100" cy="100" rx="62" ry="44" />
          <line x1="38" y1="100" x2="162" y2="100" />
          <g>
            <ellipse cx="100" cy="100" rx="14" ry="62" />
            <ellipse cx="100" cy="100" rx="38" ry="62" />
            <line x1="100" y1="38" x2="100" y2="162" />
            <animateTransform attributeName="transform" type="translate" values="-24 0;24 0;-24 0" dur="8s" repeatCount="indefinite" />
          </g>
          <g stroke="none">
            <path d="M100 100 L162 86 A64 64 0 0 1 162 114 Z" fill="url(#gl-sweep)">
              <animateTransform attributeName="transform" type="rotate" from="0 100 100" to="360 100 100" dur="3s" repeatCount="indefinite" />
            </path>
          </g>
        </g>

        {POINTS.map(([x, y, begin]) => (
          <g key={x}>
            <circle cx={x} cy={y} r="2.8" fill="#facc15" />
            <circle cx={x} cy={y} r="3" fill="none" stroke="#facc15" strokeWidth="1.2">
              <animate attributeName="r" values="3;13" dur="2s" begin={begin} repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.9;0" dur="2s" begin={begin} repeatCount="indefinite" />
            </circle>
          </g>
        ))}

        <g transform="rotate(-22 100 100)">
          <ellipse cx="100" cy="100" rx="92" ry="30" fill="none" stroke="#e0f2fe" strokeOpacity="0.5" strokeWidth="0.8" strokeDasharray="3 5" />
          <g>
            <rect x="-7" y="-2.5" width="14" height="5" rx="1" fill="#e0f2fe" />
            <rect x="-13" y="-1.5" width="5" height="3" fill="#38bdf8" />
            <rect x="8" y="-1.5" width="5" height="3" fill="#38bdf8" />
            <animateMotion dur="4.5s" repeatCount="indefinite" path="M192 100 A92 30 0 1 1 8 100 A92 30 0 1 1 192 100" />
          </g>
        </g>
      </svg>

      <p key={step} className="animate-in fade-in slide-in-from-bottom-1 font-mono text-sm tracking-wide text-muted-foreground duration-500">
        {steps[step]}
        <span className="inline-block w-6 text-left after:animate-pulse after:content-['...']" />
      </p>
    </div>
  )
}
