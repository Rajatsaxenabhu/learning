'use client'

import { useEffect, useRef } from 'react'
import 'ol/ol.css'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import ImageLayer from 'ol/layer/Image'
import OSM from 'ol/source/OSM'
import ImageWMS from 'ol/source/ImageWMS'
import { cn } from '@/lib/utils'
import { DEFAULT_LAYERS, INDIA_EXTENT, WMS_URL, outlineSld, type WmsLayer } from './wms'

type Props = {
  /** WMS layers drawn over the basemap. Defaults to the state boundaries. */
  layers?: WmsLayer[]
  /** Initial extent [minX, minY, maxX, maxY] in EPSG:3857. */
  extent?: [number, number, number, number]
  basemap?: boolean
  className?: string
}

function createWmsLayer(config: WmsLayer) {
  return new ImageLayer({
    visible: config.visible ?? true,
    opacity: config.opacity ?? 1,
    source: new ImageWMS({
      url: config.url ?? WMS_URL,
      params: {
        LAYERS: config.layer,
        STYLES: '',
        FORMAT: 'image/png',
        TRANSPARENT: true,
        VERSION: '1.3.0',
        SLD_BODY: config.sld ?? outlineSld(config.layer, config.color, config.strokeWidth),
      },
      ratio: 1,
      crossOrigin: 'anonymous',
    }),
  })
}

/** Reusable OpenLayers map: OSM basemap plus any number of WMS layers. */
export function OlMap({ layers = DEFAULT_LAYERS, extent = INDIA_EXTENT, basemap = true, className }: Props) {
  const target = useRef<HTMLDivElement>(null)
  const mapRef = useRef<Map | null>(null)
  const wmsLayers = useRef<ImageLayer<ImageWMS>[]>([])

  // create the map once
  useEffect(() => {
    if (!target.current) return
    const map = new Map({
      target: target.current,
      layers: basemap ? [new TileLayer({ source: new OSM() })] : [],
      view: new View({ center: [0, 0], zoom: 2 }),
      controls: [],
    })
    map.updateSize()
    map.getView().fit(extent, { size: map.getSize() })
    mapRef.current = map
    // keep the canvas sized when the surrounding layout changes
    const observer = new ResizeObserver(() => map.updateSize())
    observer.observe(target.current)
    return () => {
      observer.disconnect()
      map.setTarget(undefined)
      mapRef.current = null
      wmsLayers.current = []
    }
    // the map is created once; layers are synced by the effect below
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // keep the WMS layers in sync with props
  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    wmsLayers.current.forEach((l) => map.removeLayer(l))
    wmsLayers.current = layers.map(createWmsLayer)
    wmsLayers.current.forEach((l) => map.addLayer(l))
  }, [layers])

  return <div ref={target} className={cn('size-full min-h-64 bg-muted', className)} />
}
