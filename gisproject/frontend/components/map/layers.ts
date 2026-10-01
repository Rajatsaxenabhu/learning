import GeoJSON from 'ol/format/GeoJSON'
import TileLayer from 'ol/layer/Tile'
import VectorLayer from 'ol/layer/Vector'
import XYZ from 'ol/source/XYZ'
import VectorSource from 'ol/source/Vector'
import { Fill, Stroke, Style } from 'ol/style'
import type BaseLayer from 'ol/layer/Base'

export type MapLayerData = {
  id: string
  type: 'geojson' | 'xyz'
  name: string
  geojson?: object | null
  url?: string | null
}

const footprintStyle = new Style({
  stroke: new Stroke({ color: '#f59e0b', width: 2 }),
  fill: new Fill({ color: 'rgba(245, 158, 11, 0.08)' }),
})

export function createOverlay(data: MapLayerData): BaseLayer | null {
  if (data.type === 'xyz' && data.url) {
    return new TileLayer({
      source: new XYZ({ url: data.url, crossOrigin: 'anonymous', maxZoom: 18 }),
    })
  }
  if (data.type === 'geojson' && data.geojson) {
    return new VectorLayer({
      style: footprintStyle,
      source: new VectorSource({
        features: new GeoJSON().readFeatures(
          { type: 'Feature', geometry: data.geojson, properties: { name: data.name } },
          { dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857' },
        ),
      }),
    })
  }
  return null
}
