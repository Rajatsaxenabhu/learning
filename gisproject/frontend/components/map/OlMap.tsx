'use client'

import { useEffect, useRef } from 'react'
import 'ol/ol.css'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import ImageLayer from 'ol/layer/Image'
import OSM from 'ol/source/OSM'
import { transformExtent } from 'ol/proj'
import type BaseLayer from 'ol/layer/Base'
import ImageWMS from 'ol/source/ImageWMS'
import { cn } from '@/lib/utils'
import { createOverlay, type MapLayerData } from './layers'
import { DEFAULT_LAYERS, INDIA_EXTENT, WMS_URL, outlineSld, type WmsLayer } from './wms'

type Props = {
  layers?: WmsLayer[]
  extent?: [number, number, number, number]
  overlays?: MapLayerData[]
  fitTo?: [number, number, number, number] | null
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

export function OlMap({ layers = DEFAULT_LAYERS, extent = INDIA_EXTENT, overlays, fitTo, basemap = true, className }: Props) {
  const target = useRef<HTMLDivElement>(null)
  const mapRef = useRef<Map | null>(null)
  const wmsLayers = useRef<ImageLayer<ImageWMS>[]>([])
  const overlayLayers = useRef<BaseLayer[]>([])

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
    const observer = new ResizeObserver(() => map.updateSize())
    observer.observe(target.current)
    return () => {
      observer.disconnect()
      map.setTarget(undefined)
      mapRef.current = null
      wmsLayers.current = []
      overlayLayers.current = []
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    wmsLayers.current.forEach((l) => map.removeLayer(l))
    wmsLayers.current = layers.map(createWmsLayer)
    wmsLayers.current.forEach((l) => map.addLayer(l))
  }, [layers])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    overlayLayers.current.forEach((l) => map.removeLayer(l))
    const sorted = [...(overlays ?? [])].sort((a, b) => Number(b.type === 'xyz') - Number(a.type === 'xyz'))
    overlayLayers.current = sorted.map(createOverlay).filter((l): l is BaseLayer => l !== null)
    overlayLayers.current.forEach((l) => map.addLayer(l))
  }, [overlays])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !fitTo) return
    map.getView().fit(transformExtent(fitTo, 'EPSG:4326', 'EPSG:3857'), {
      size: map.getSize(),
      padding: [24, 24, 24, 24],
      maxZoom: 14,
      duration: 500,
    })
  }, [fitTo])

  return <div ref={target} className={cn('size-full min-h-64 bg-muted', className)} />
}
