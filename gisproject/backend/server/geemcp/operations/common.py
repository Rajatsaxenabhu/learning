from datetime import datetime, timezone

import ee
from mcp.server.mcpserver.exceptions import ToolError

from server.geemcp.schemas.imagery import (
    BoundingBox,
    PropertyFilter,
)


DEPRECATED_COLLECTIONS = {
    "COPERNICUS/S2_SR": "COPERNICUS/S2_SR_HARMONIZED",
    "COPERNICUS/S2": "COPERNICUS/S2_HARMONIZED",
}


SENTINEL2_WAVELENGTHS = {
    "B1": 443,
    "B2": 490,
    "B3": 560,
    "B4": 665,
    "B5": 705,
    "B6": 740,
    "B7": 783,
    "B8": 842,
    "B8A": 865,
    "B9": 945,
    "B11": 1610,
    "B12": 2190,
}

LANDSAT_WAVELENGTHS = {
    "SR_B1": 443,
    "SR_B2": 482,
    "SR_B3": 561,
    "SR_B4": 655,
    "SR_B5": 865,
    "SR_B6": 1609,
    "SR_B7": 2201,
}

SENTINEL2 = {
    "cloud": "CLOUDY_PIXEL_PERCENTAGE",
    "index_bands": {
        "blue": "B2",
        "green": "B3",
        "red": "B4",
        "nir": "B8",
        "swir1": "B11",
        "swir2": "B12",
    },
    "scale": (0.0001, 0.0),
    "pixel_m": 20,
    "vis": {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000},
    "wavelengths": SENTINEL2_WAVELENGTHS,
}

LANDSAT = {
    "cloud": "CLOUD_COVER",
    "index_bands": {
        "blue": "SR_B2",
        "green": "SR_B3",
        "red": "SR_B4",
        "nir": "SR_B5",
        "swir1": "SR_B6",
        "swir2": "SR_B7",
    },
    "scale": (0.0000275, -0.2),
    "pixel_m": 30,
    "vis": {
        "bands": ["SR_B4", "SR_B3", "SR_B2"],
        "min": 7273,
        "max": 18182,
    },
    "wavelengths": LANDSAT_WAVELENGTHS,
}

PROFILES = {
    "COPERNICUS/S2": SENTINEL2,
    "LANDSAT/LC08/C02/T1_L2": LANDSAT,
    "LANDSAT/LC09/C02/T1_L2": LANDSAT,
}

OPERATORS = {
    "eq": ee.Filter.eq,
    "neq": ee.Filter.neq,
    "gt": ee.Filter.gt,
    "gte": ee.Filter.gte,
    "lt": ee.Filter.lt,
    "lte": ee.Filter.lte,
}


def resolve_collection(name: str) -> str:

    return DEPRECATED_COLLECTIONS.get(name, name)


def profile(asset_id: str) -> dict | None:

    for prefix, value in PROFILES.items():

        if asset_id.startswith(prefix):
            return value

    return None


def to_date(millis: int | None) -> str | None:

    if millis is None:
        return None

    return datetime.fromtimestamp(
        millis / 1000,
        tz=timezone.utc,
    ).strftime("%Y-%m-%d")


def rectangle(bbox: BoundingBox) -> ee.Geometry:

    return ee.Geometry.Rectangle(
        [
            bbox.min_lon,
            bbox.min_lat,
            bbox.max_lon,
            bbox.max_lat,
        ]
    )


def footprint(feature: dict) -> dict | None:

    ring = feature.get("properties", {}).get("system:footprint")

    if not ring:
        return feature.get("geometry")

    return {
        "type": "Polygon",
        "coordinates": [ring["coordinates"]],
    }


def extent_of(geometries: list[dict]) -> list[float] | None:

    points = []

    def collect(coordinates):

        if coordinates and isinstance(coordinates[0], (int, float)):
            points.append(coordinates)
            return

        for item in coordinates:
            collect(item)

    for geometry in geometries:
        collect(geometry["coordinates"])

    if not points:
        return None

    lons = [p[0] for p in points]
    lats = [p[1] for p in points]

    return [min(lons), min(lats), max(lons), max(lats)]


def tile_url(image: ee.Image, vis: dict) -> str:

    return image.getMapId(vis)["tile_fetcher"].url_format


def property_filter(item: PropertyFilter) -> ee.Filter:

    if item.operator == "contains":
        return ee.Filter.stringContains(item.name, item.value)

    try:
        value = float(item.value)
    except ValueError:
        value = item.value

    return OPERATORS[item.operator](item.name, value)


def build_collection(
    collection: str,
    bbox: BoundingBox | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    max_cloud_percentage: float | None = None,
    property_filters: list[PropertyFilter] | None = None,
) -> ee.ImageCollection:

    images = ee.ImageCollection(collection)

    if bbox:
        images = images.filterBounds(rectangle(bbox))

    if bool(start_date) != bool(end_date):
        raise ToolError(
            "start_date and end_date must be given together."
        )

    if start_date:
        images = images.filterDate(start_date, end_date)

    if max_cloud_percentage is not None:

        known = profile(collection)

        if not known:
            raise ToolError(
                f"Cloud filtering is not supported for {collection}."
            )

        images = images.filter(
            ee.Filter.lte(
                known["cloud"],
                max_cloud_percentage,
            )
        )

    for item in property_filters or []:
        images = images.filter(property_filter(item))

    return images.sort("system:time_start")
