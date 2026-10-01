export type WmsLayer = {
  id: string
  /** GeoServer layer name, e.g. `workspace:layer` */
  layer: string
  url?: string
  visible?: boolean
  opacity?: number
  /** Outline colour used by the generated SLD. Ignored if `sld` is given. */
  color?: string
  strokeWidth?: number
  /** Full SLD body; overrides the generated outline style. */
  sld?: string
}

export const WMS_URL = 'https://geo.slcrdss.in/geoserver/wms'

/** Initial view over India, as [minX, minY, maxX, maxY] in EPSG:3857. */
export const INDIA_EXTENT: [number, number, number, number] = [7594599, 814332, 9985619, 4837510]

/** SLD that draws polygon / line outlines only (no fill). */
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
