import { create } from 'zustand'
import type { MapLayerData } from '@/components/map/layers'

type MapState = {
  layers: MapLayerData[]
  extent: [number, number, number, number] | null
  show: (layers: MapLayerData[], extent: MapState['extent']) => void
  clear: () => void
}

export const useMapStore = create<MapState>((set) => ({
  layers: [],
  extent: null,
  show: (layers, extent) => set({ layers, extent }),
  clear: () => set({ layers: [], extent: null }),
}))
