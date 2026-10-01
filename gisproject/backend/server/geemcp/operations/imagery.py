import ee

from server.geemcp.schemas.imagery import (
    SatelliteSearchRequest,
)


DEPRECATED_COLLECTIONS = {
    "COPERNICUS/S2_SR": "COPERNICUS/S2_SR_HARMONIZED",
    "COPERNICUS/S2": "COPERNICUS/S2_HARMONIZED",
}


def search_satellite_images(
    request: SatelliteSearchRequest,
) -> dict:

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

    images = collection.limit(
        request.limit
    ).getInfo()["features"]

    results = []

    for image in images:

        properties = image.get("properties", {})

        results.append(
            {
                "id": image.get("id"),
                "date": properties.get(
                    "system:time_start"
                ),
                "cloud_percentage": properties.get(
                    "CLOUDY_PIXEL_PERCENTAGE"
                ),
            }
        )

    return {
        "collection": request.collection,
        "count": count,
        "images": results,
    }
