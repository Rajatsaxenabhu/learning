from server.geemcp.server import mcp, READ_ONLY
from server.geemcp.schemas.imagery import (
    CollectionInfo,
    CollectionRequest,
    CompositeRequest,
    CompositeResult,
    SpectralIndexRequest,
    SpectralIndexResult,
)
from server.geemcp.operations import collection


@mcp.tool(
    name="get_collection_info",
    description=(
        "Get an Earth Engine image collection's size, date range, "
        "bands and filterable property names."
    ),
    annotations=READ_ONLY,
)
def get_collection_info_tool(
    payload: CollectionRequest,
) -> CollectionInfo:

    return collection.get_collection_info(payload)


@mcp.tool(
    name="create_composite",
    description=(
        "Combine images over an area and date range into one "
        "median, mean, mosaic, minimum or maximum composite "
        "and show it on the map."
    ),
    annotations=READ_ONLY,
)
def create_composite_tool(
    payload: CompositeRequest,
) -> CompositeResult:

    return collection.create_composite(payload)


@mcp.tool(
    name="calculate_spectral_index",
    description=(
        "Calculate NDVI, NDWI, NDBI, EVI, SAVI, NDMI or NBR over an "
        "area and date range from Sentinel-2 or Landsat 8/9, "
        "show it on the map and return its statistics."
    ),
    annotations=READ_ONLY,
)
def calculate_spectral_index_tool(
    payload: SpectralIndexRequest,
) -> SpectralIndexResult:

    return collection.calculate_spectral_index(payload)
