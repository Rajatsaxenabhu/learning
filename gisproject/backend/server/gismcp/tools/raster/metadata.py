from server.gismcp.operations.raster.metadata import (
    get_raster_metadata,
    get_raster_crs,
    get_raster_bounds,
    get_raster_resolution,
    get_raster_band_info,
)
from server.gismcp.schemas.raster.metadata import (
    GetRasterMetadataInput,
    GetRasterMetadataOutput,
    GetRasterCrsInput,
    GetRasterCrsOutput,
    GetRasterBoundsInput,
    GetRasterBoundsOutput,
    GetRasterResolutionInput,
    GetRasterResolutionOutput,
    GetRasterBandInfoInput,
    GetRasterBandInfoOutput,
)
from server.gismcp.server import mcp


@mcp.tool(title="get_raster_metadata_tool")
def get_raster_metadata_tool(
    payload: GetRasterMetadataInput,
) -> GetRasterMetadataOutput:
    """Get general metadata of a raster: size, bands, CRS, bounds, resolution and NoData."""

    return get_raster_metadata(payload)


@mcp.tool(title="get_raster_crs_tool")
def get_raster_crs_tool(
    payload: GetRasterCrsInput,
) -> GetRasterCrsOutput:
    """Get the coordinate reference system of a raster."""

    return get_raster_crs(payload)


@mcp.tool(title="get_raster_bounds_tool")
def get_raster_bounds_tool(
    payload: GetRasterBoundsInput,
) -> GetRasterBoundsOutput:
    """Get the bounding box of a raster in its own CRS."""

    return get_raster_bounds(payload)


@mcp.tool(title="get_raster_resolution_tool")
def get_raster_resolution_tool(
    payload: GetRasterResolutionInput,
) -> GetRasterResolutionOutput:
    """Get the pixel size (resolution) of a raster in CRS units."""

    return get_raster_resolution(payload)


@mcp.tool(title="get_raster_band_info_tool")
def get_raster_band_info_tool(
    payload: GetRasterBandInfoInput,
) -> GetRasterBandInfoOutput:
    """Get data type, NoData value and description of every band in a raster."""

    return get_raster_band_info(payload)
