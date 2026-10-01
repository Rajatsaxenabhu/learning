from server.geemcp.server import mcp, READ_ONLY
from server.geemcp.schemas.imagery import (
    FilterCollectionRequest,
    ImageBandsResult,
    ImageMetadataResult,
    ImageRequest,
    SatelliteSearchRequest,
    SatelliteSearchResult,
)
from server.geemcp.operations import imagery


@mcp.tool(
    name="search_satellite_images",
    description=(
        "Search Google Earth Engine satellite imagery "
        "for a geographic bounding box and date range."
    ),
    annotations=READ_ONLY,
)
def search_satellite_images_tool(
    payload: SatelliteSearchRequest,
) -> SatelliteSearchResult:

    return imagery.search_satellite_images(payload)


@mcp.tool(
    name="filter_image_collection",
    description=(
        "Filter an Earth Engine image collection by optional area, "
        "dates, cloud percentage and image properties "
        "(for example MGRS_TILE or SPACECRAFT_NAME)."
    ),
    annotations=READ_ONLY,
)
def filter_image_collection_tool(
    payload: FilterCollectionRequest,
) -> SatelliteSearchResult:

    return imagery.filter_image_collection(payload)


@mcp.tool(
    name="get_image_metadata",
    description=(
        "Get acquisition date, cloud cover, CRS, bounds and key "
        "properties of one Earth Engine image from its full image ID."
    ),
    annotations=READ_ONLY,
)
def get_image_metadata_tool(
    payload: ImageRequest,
) -> ImageMetadataResult:

    return imagery.get_image_metadata(payload)


@mcp.tool(
    name="get_image_bands",
    description=(
        "List the bands of one Earth Engine image with data type, "
        "pixel size and wavelength where known."
    ),
    annotations=READ_ONLY,
)
def get_image_bands_tool(
    payload: ImageRequest,
) -> ImageBandsResult:

    return imagery.get_image_bands(payload)
