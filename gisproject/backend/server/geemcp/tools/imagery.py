
from server.geemcp.server import mcp, READ_ONLY
from server.geemcp.schemas.imagery import (
    SatelliteSearchRequest,
    SatelliteSearchResult,
)
from server.geemcp.operations.imagery import (
    search_satellite_images,
)


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

    return search_satellite_images(payload)

