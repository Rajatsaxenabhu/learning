export type WmsLayer = {
  id: string
  layer: string
  url?: string
  visible?: boolean
  opacity?: number
  color?: string
  strokeWidth?: number
  sld?: string
}

export const WMS_URL = 'https://geo.slcrdss.in/geoserver/wms'

export const INDIA_EXTENT: [number, number, number, number] = [7594599, 814332, 9985619, 4837510]

export function outlineSld(layer: string, color = '#22c55e', width = 2): string {
  const stroke = `<Stroke><CssParameter name="stroke">${color}</CssParameter><CssParameter name="stroke-width">${width}</CssParameter></Stroke>`
  return (
    `<?xml version="1.0" encoding="UTF-8"?>` +
    `<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld">` +
    `<NamedLayer><Name>${layer}</Name><UserStyle><FeatureTypeStyle><Rule>` +
    `<PolygonSymbolizer><Fill><CssParameter name="fill-opacity">0</CssParameter></Fill>${stroke}</PolygonSymbolizer>` +
    `<LineSymbolizer>${stroke}</LineSymbolizer>` +
    `</Rule></FeatureTypeStyle></UserStyle></NamedLayer></StyledLayerDescriptor>`
  )
}

export const DEFAULT_LAYERS: WmsLayer[] = [{ id: 'state', layer: 'vector_work:state' }]
