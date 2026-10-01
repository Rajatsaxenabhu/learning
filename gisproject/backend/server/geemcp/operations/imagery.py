from datetime import datetime, timezone

import ee

from server.geemcp.config.logging import logger
from server.geemcp.schemas.imagery import (
    ImageSummary,
    MapLayer,
    MapPayload,
    SatelliteSearchRequest,
    SatelliteSearchResult,
    SatelliteSearchSummary,
)


DEPRECATED_COLLECTIONS = {
    "COPERNICUS/S2_SR": "COPERNICUS/S2_SR_HARMONIZED",
    "COPERNICUS/S2": "COPERNICUS/S2_HARMONIZED",
}


SENTINEL2_RGB = {
    "bands": ["B4", "B3", "B2"],
    "min": 0,
    "max": 3000,
}


def _to_date(millis: int | None) -> str | None:

    if millis is None:
        return None

    return datetime.fromtimestamp(
        millis / 1000,
        tz=timezone.utc,
    ).strftime("%Y-%m-%d")


def _footprint(feature: dict) -> dict | None:

    ring = feature.get("properties", {}).get("system:footprint")

    if not ring:
        return feature.get("geometry")

    return {
        "type": "Polygon",
        "coordinates": [ring["coordinates"]],
    }


def _tile_url(image_id: str) -> str:

    map_id = ee.Image(image_id).getMapId(SENTINEL2_RGB)

    return map_id["tile_fetcher"].url_format


def search_satellite_images(
    request: SatelliteSearchRequest,
) -> SatelliteSearchResult:

    bbox = request.bbox

    request.collection = DEPRECATED_COLLECTIONS.get(
        request.collection,
        request.collection,
    )

    geometry = ee.Geometry.Rectangle(
        [
            bbox.min_lon,
            bbox.min_lat,
            bbox.max_lon,
            bbox.max_lat,
        ]
    )

    collection = (
        ee.ImageCollection(request.collection)
        .filterBounds(geometry)
        .filterDate(
            request.start_date,
            request.end_date,
        )
        .filter(
            ee.Filter.lte(
                "CLOUDY_PIXEL_PERCENTAGE",
                request.max_cloud_percentage,
            )
        )
        .sort("system:time_start")
    )

    count = collection.size().getInfo()

    features = collection.limit(
        request.limit
    ).getInfo()["features"]

    images = []
    layers = []

    for feature in features:

        properties = feature.get("properties", {})

        image_id = feature["id"]

        images.append(
            ImageSummary(
                id=image_id,
                date=_to_date(
                    properties.get("system:time_start")
                ),
                cloud_percentage=properties.get(
                    "CLOUDY_PIXEL_PERCENTAGE"
                ),
            )
        )

        footprint = _footprint(feature)

        if footprint:
            layers.append(
                MapLayer(
                    id=f"footprint:{image_id}",
                    type="geojson",
                    name=image_id.rsplit("/", 1)[-1],
                    geojson=footprint,
                )
            )

    shown = None

    best = min(
        (i for i in images if i.cloud_percentage is not None),
        key=lambda i: i.cloud_percentage,
        default=None,
    )

    if best and request.collection.startswith("COPERNICUS/S2"):

        try:
            layers.append(
                MapLayer(
                    id=f"tiles:{best.id}",
                    type="xyz",
                    name=f"{best.date} ({best.cloud_percentage:.1f}% cloud)",
                    url=_tile_url(best.id),
                )
            )
            shown = best.id

        except ee.EEException:
            logger.exception(
                "could not build tiles for %s", best.id
            )

    return SatelliteSearchResult(
        summary=SatelliteSearchSummary(
            collection=request.collection,
            count=count,
            images=images,
            shown_on_map=shown,
        ),
        map=MapPayload(
            layers=layers,
            extent=[
                bbox.min_lon,
                bbox.min_lat,
                bbox.max_lon,
                bbox.max_lat,
            ],
        ),
    )
