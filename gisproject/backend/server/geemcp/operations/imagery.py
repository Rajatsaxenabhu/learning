import ee
from mcp.server.mcpserver.exceptions import ToolError

from server.geemcp.config.logging import logger
from server.geemcp.operations.common import (
    build_collection,
    extent_of,
    footprint,
    profile,
    resolve_collection,
    tile_url,
    to_date,
)
from server.geemcp.schemas.imagery import (
    BandInfo,
    FilterCollectionRequest,
    ImageBandsResult,
    ImageMetadata,
    ImageMetadataResult,
    ImageRequest,
    ImageSummary,
    MapLayer,
    MapPayload,
    SatelliteSearchRequest,
    SatelliteSearchResult,
    SatelliteSearchSummary,
)


METADATA_KEYS = (
    "SPACECRAFT_NAME",
    "SPACECRAFT_ID",
    "PRODUCT_ID",
    "LANDSAT_PRODUCT_ID",
    "MGRS_TILE",
    "WRS_PATH",
    "WRS_ROW",
    "SENSING_ORBIT_NUMBER",
    "PROCESSING_BASELINE",
    "SUN_ELEVATION",
    "MEAN_SOLAR_ZENITH_ANGLE",
)


def _search(
    collection_id: str,
    images: ee.ImageCollection,
    limit: int,
    bbox=None,
) -> SatelliteSearchResult:

    known = profile(collection_id)

    cloud_property = known["cloud"] if known else None

    count = images.size().getInfo()

    features = images.limit(limit).getInfo()["features"]

    summaries = []
    layers = []
    footprints = []

    for feature in features:

        properties = feature.get("properties", {})

        image_id = feature["id"]

        summaries.append(
            ImageSummary(
                id=image_id,
                date=to_date(
                    properties.get("system:time_start")
                ),
                cloud_percentage=properties.get(cloud_property),
            )
        )

        outline = footprint(feature)

        if outline:
            footprints.append(outline)
            layers.append(
                MapLayer(
                    id=f"footprint:{image_id}",
                    type="geojson",
                    name=image_id.rsplit("/", 1)[-1],
                    geojson=outline,
                )
            )

    shown = None

    if summaries and known:

        best = min(
            summaries,
            key=lambda i: (
                i.cloud_percentage
                if i.cloud_percentage is not None
                else float("inf")
            ),
        )

        try:
            layers.append(
                MapLayer(
                    id=f"tiles:{best.id}",
                    type="xyz",
                    name=f"{best.date}",
                    url=tile_url(
                        ee.Image(best.id),
                        known["vis"],
                    ),
                )
            )
            shown = best.id

        except ee.EEException:
            logger.exception(
                "could not build tiles for %s", best.id
            )

    extent = (
        [bbox.min_lon, bbox.min_lat, bbox.max_lon, bbox.max_lat]
        if bbox
        else extent_of(footprints)
    )

    return SatelliteSearchResult(
        summary=SatelliteSearchSummary(
            collection=collection_id,
            count=count,
            images=summaries,
            shown_on_map=shown,
        ),
        map=MapPayload(
            layers=layers,
            extent=extent,
        ),
    )


def search_satellite_images(
    request: SatelliteSearchRequest,
) -> SatelliteSearchResult:

    collection = resolve_collection(request.collection)

    images = build_collection(
        collection,
        bbox=request.bbox,
        start_date=request.start_date,
        end_date=request.end_date,
        max_cloud_percentage=request.max_cloud_percentage,
    )

    return _search(
        collection,
        images,
        request.limit,
        request.bbox,
    )


def filter_image_collection(
    request: FilterCollectionRequest,
) -> SatelliteSearchResult:

    collection = resolve_collection(request.collection)

    images = build_collection(
        collection,
        bbox=request.bbox,
        start_date=request.start_date,
        end_date=request.end_date,
        max_cloud_percentage=request.max_cloud_percentage,
        property_filters=request.property_filters,
    )

    return _search(
        collection,
        images,
        request.limit,
        request.bbox,
    )


def get_image_metadata(
    request: ImageRequest,
) -> ImageMetadataResult:

    image = ee.Image(request.image_id)

    try:
        info = image.getInfo()
    except ee.EEException as exc:
        raise ToolError(
            f"Could not load image {request.image_id}: {exc}"
        ) from exc

    properties = info.get("properties", {})

    bands = info.get("bands", [])

    known = profile(request.image_id)

    ring = footprint(info)

    bounds = extent_of([ring]) if ring else None

    layers = []

    if ring:
        layers.append(
            MapLayer(
                id=f"footprint:{request.image_id}",
                type="geojson",
                name=request.image_id.rsplit("/", 1)[-1],
                geojson=ring,
            )
        )

    return ImageMetadataResult(
        summary=ImageMetadata(
            id=request.image_id,
            date=to_date(properties.get("system:time_start")),
            cloud_percentage=(
                properties.get(known["cloud"]) if known else None
            ),
            crs=bands[0].get("crs") if bands else None,
            bounds=bounds,
            band_count=len(bands),
            properties={
                key: properties[key]
                for key in METADATA_KEYS
                if key in properties
            },
        ),
        map=MapPayload(
            layers=layers,
            extent=bounds,
        ),
    )


def get_image_bands(
    request: ImageRequest,
) -> ImageBandsResult:

    try:
        info = ee.Image(request.image_id).getInfo()
    except ee.EEException as exc:
        raise ToolError(
            f"Could not load image {request.image_id}: {exc}"
        ) from exc

    known = profile(request.image_id)

    wavelengths = known["wavelengths"] if known else {}

    bands = []

    for band in info.get("bands", []):

        crs = band.get("crs")

        transform = band.get("crs_transform")

        projected = bool(crs) and crs != "EPSG:4326"

        bands.append(
            BandInfo(
                name=band["id"],
                data_type=band.get("data_type", {}).get(
                    "precision", "unknown"
                ),
                scale_m=(
                    abs(transform[0])
                    if projected and transform
                    else None
                ),
                wavelength_nm=wavelengths.get(band["id"]),
            )
        )

    return ImageBandsResult(
        image_id=request.image_id,
        bands=bands,
    )
