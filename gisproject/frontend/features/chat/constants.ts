import { Boxes, Grid3x3, Layers, Map, Ruler, ScanLine, type LucideIcon } from 'lucide-react'

export const gradientBg =
  'bg-[radial-gradient(60rem_40rem_at_15%_-10%,oklch(0.93_0.06_165/0.55),transparent),radial-gradient(50rem_35rem_at_100%_0%,oklch(0.92_0.05_240/0.5),transparent)] dark:bg-[radial-gradient(60rem_40rem_at_15%_-10%,oklch(0.45_0.1_165/0.28),transparent),radial-gradient(50rem_35rem_at_100%_0%,oklch(0.4_0.12_260/0.25),transparent)] bg-background'

export const capabilities: { icon: LucideIcon; title: string; hint: string; prompt: string }[] = [
  { icon: Ruler, title: 'Geometry', hint: 'Area, buffer, intersect', prompt: 'Buffer this point by 500 m and calculate the area' },
  { icon: Map, title: 'Projection', hint: 'CRS and UTM zones', prompt: 'Which UTM zone is longitude 77.2, latitude 28.6 in?' },
  { icon: Layers, title: 'Vector data', hint: 'Layers, filters, queries', prompt: 'List the layers and schema of my vector file' },
  { icon: ScanLine, title: 'Raster info', hint: 'Metadata, CRS, bands', prompt: 'Show the metadata and band info of my raster' },
  { icon: Grid3x3, title: 'Raster stats', hint: 'Histogram, percentiles', prompt: 'Calculate statistics and a histogram for my raster' },
  { icon: Boxes, title: 'Processing', hint: 'Clip, reproject, merge', prompt: 'Clip my raster to a polygon and reproject it to EPSG:4326' },
]
