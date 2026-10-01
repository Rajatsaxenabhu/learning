import ee
from mcp.server.mcpserver.exceptions import ToolError

from server.geemcp.operations.common import (
    build_collection,
    profile,
    rectangle,
    resolve_collection,
    tile_url,
    to_date,
)
from server.geemcp.schemas.imagery import (
    CollectionInfo,
    CollectionRequest,
    CompositeRequest,
    CompositeResult,
    CompositeSummary,
    IndexStats,
    MapLayer,
    MapPayload,
    SpectralIndexRequest,
    SpectralIndexResult,
    SpectralIndexSummary,
)


HIDDEN_PROPERTIES = {"system:footprint"}

REDUCERS = {
    "median": lambda images: images.median(),
    "mean": lambda images: images.mean(),
    "mosaic": lambda images: images.mosaic(),
    "min": lambda images: images.min(),
    "max": lambda images: images.max(),
}

VEGETATION = ["#a50026", "#f46d43", "#fee08b", "#a6d96a", "#1a9850"]
WATER = ["#8c510a", "#d8b365", "#f6e8c3", "#80cdc1", "#01665e"]
BUILT_UP = ["#1a9850", "#a6d96a", "#fee08b", "#f46d43", "#a50026"]

INDICES = {
    "NDVI": ("(NIR - RED) / (NIR + RED)", -0.2, 0.9, VEGETATION),
    "NDWI": ("(GREEN - NIR) / (GREEN + NIR)", -0.5, 0.5, WATER),
    "NDBI": ("(SWIR1 - NIR) / (SWIR1 + NIR)", -0.5, 0.5, BUILT_UP),
    "EVI": (
        "2.5 * (NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1)",
        -0.2,
        1.0,
        VEGETATION,
    ),
    "SAVI": ("1.5 * (NIR - RED) / (NIR + RED + 0.5)", -0.2, 1.0, VEGETATION),
    "NDMI": ("(NIR - SWIR1) / (NIR + SWIR1)", -0.5, 0.8, WATER),
    "NBR": ("(NIR - SWIR2) / (NIR + SWIR2)", -0.5, 1.0, VEGETATION),
}


def _require(images: ee.ImageCollection) -> int:

    count = images.size().getInfo()

    if count == 0:
        raise ToolError(
            "No images match these filters. Try a wider area, "
            "longer date range or higher cloud limit."
        )

    return count


def get_collection_info(
    request: CollectionRequest,
) -> CollectionInfo:

    collection = resolve_collection(request.collection)

    images = ee.ImageCollection(collection)

    try:
        count = images.size().getInfo()
    except ee.EEException as exc:
        raise ToolError(
            f"Could not load collection {collection}: {exc}"
        ) from exc

    if count == 0:
        raise ToolError(f"Collection {collection} has no images.")

    first = images.first().getInfo()

    known = profile(collection)

    return CollectionInfo(
        collection=collection,
        image_count=count,
        start_date=to_date(
            images.aggregate_min("system:time_start").getInfo()
        ),
        end_date=to_date(
            images.aggregate_max("system:time_start").getInfo()
        ),
        bands=[band["id"] for band in first.get("bands", [])],
        properties=sorted(
            key
            for key in first.get("properties", {})
            if key not in HIDDEN_PROPERTIES
        ),
        cloud_property=known["cloud"] if known else None,
        preview_supported=known is not None,
    )


def create_composite(
    request: CompositeRequest,
) -> CompositeResult:

    collection = resolve_collection(request.collection)

    images = build_collection(
        collection,
        bbox=request.bbox,
        start_date=request.start_date,
        end_date=request.end_date,
        max_cloud_percentage=request.max_cloud_percentage,
    )

    count = _require(images)

    known = profile(collection)

    vis = dict(known["vis"]) if known else {}

    if request.bands:
        vis["bands"] = request.bands

    if request.min is not None:
        vis["min"] = request.min

    if request.max is not None:
        vis["max"] = request.max

    if not {"bands", "min", "max"} <= vis.keys():
        raise ToolError(
            f"No default display for {collection}. "
            "Give bands (three names), min and max."
        )

    image = REDUCERS[request.method](images).clip(
        rectangle(request.bbox)
    )

    bbox = request.bbox

    return CompositeResult(
        summary=CompositeSummary(
            collection=collection,
            method=request.method,
            image_count=count,
            start_date=request.start_date,
            end_date=request.end_date,
            bands=vis["bands"],
        ),
        map=MapPayload(
            layers=[
                MapLayer(
                    id=(
                        f"composite:{collection}:{request.method}:"
                        f"{request.start_date}:{request.end_date}"
                    ),
                    type="xyz",
                    name=f"{request.method} composite",
                    url=tile_url(image, vis),
                )
            ],
            extent=[
                bbox.min_lon,
                bbox.min_lat,
                bbox.max_lon,
                bbox.max_lat,
            ],
        ),
    )


def _index_image(
    name: str,
    image: ee.Image,
    bands: dict,
    scale: tuple[float, float],
) -> ee.Image:

    multiplier, offset = scale

    reflectance = (
        image.select(list(bands.values()))
        .multiply(multiplier)
        .add(offset)
    )

    formula = INDICES[name][0]

    return reflectance.expression(
        formula,
        {
            label.upper(): reflectance.select(band)
            for label, band in bands.items()
        },
    ).rename(name)


def calculate_spectral_index(
    request: SpectralIndexRequest,
) -> SpectralIndexResult:

    collection = resolve_collection(request.collection)

    known = profile(collection)

    if not known:
        raise ToolError(
            "Spectral indices need Sentinel-2 "
            "(COPERNICUS/S2_SR_HARMONIZED) or Landsat 8/9 Level-2 "
            "(LANDSAT/LC08/C02/T1_L2, LANDSAT/LC09/C02/T1_L2)."
        )

    images = build_collection(
        collection,
        bbox=request.bbox,
        start_date=request.start_date,
        end_date=request.end_date,
        max_cloud_percentage=request.max_cloud_percentage,
    )

    count = _require(images)

    geometry = rectangle(request.bbox)

    composite = REDUCERS[request.method](images)

    index = _index_image(
        request.index,
        composite,
        known["index_bands"],
        known["scale"],
    ).clip(geometry)

    formula, low, high, palette = INDICES[request.index]

    reducer = (
        ee.Reducer.mean()
        .combine(ee.Reducer.min(), sharedInputs=True)
        .combine(ee.Reducer.max(), sharedInputs=True)
        .combine(ee.Reducer.stdDev(), sharedInputs=True)
    )

    values = index.reduceRegion(
        reducer=reducer,
        geometry=geometry,
        scale=known["pixel_m"],
        maxPixels=1_000_000_000,
        bestEffort=True,
    ).getInfo()

    def stat(kind: str) -> float | None:

        value = values.get(f"{request.index}_{kind}")

        return round(value, 4) if value is not None else None

    bbox = request.bbox

    return SpectralIndexResult(
        summary=SpectralIndexSummary(
            index=request.index,
            formula=formula,
            collection=collection,
            method=request.method,
            image_count=count,
            start_date=request.start_date,
            end_date=request.end_date,
            pixel_size_m=known["pixel_m"],
            stats=IndexStats(
                mean=stat("mean"),
                min=stat("min"),
                max=stat("max"),
                std=stat("stdDev"),
            ),
        ),
        map=MapPayload(
            layers=[
                MapLayer(
                    id=(
                        f"index:{request.index}:{collection}:"
                        f"{request.start_date}:{request.end_date}"
                    ),
                    type="xyz",
                    name=f"{request.index} ({request.method})",
                    url=tile_url(
                        index,
                        {"min": low, "max": high, "palette": palette},
                    ),
                )
            ],
            extent=[
                bbox.min_lon,
                bbox.min_lat,
                bbox.max_lon,
                bbox.max_lat,
            ],
        ),
    )
