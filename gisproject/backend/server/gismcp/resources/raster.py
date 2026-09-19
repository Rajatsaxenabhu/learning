from server.gismcp.server import mcp


METADATA_TOOLS = {
    "get_raster_metadata_tool",
    "get_raster_crs_tool",
    "get_raster_bounds_tool",
    "get_raster_resolution_tool",
    "get_raster_band_info_tool",
}

STATISTICS_TOOLS = {
    "calculate_raster_statistics_tool",
    "calculate_percentiles_tool",
    "get_unique_values_tool",
    "calculate_histogram_tool",
    "get_pixel_value_tool",
    "calculate_nodata_percentage_tool",
}

PROCESSING_TOOLS = {
    "clip_raster_tool",
    "mask_raster_tool",
    "reproject_raster_tool",
    "resample_raster_tool",
    "merge_rasters_tool",
    "crop_raster_tool",
    "rasterize_vector_tool",
    "polygonize_raster_tool",
}


@mcp.resource("gis://raster/operations")
async def raster_operations() -> dict:
    """Return available raster GIS operations, grouped by category."""

    registered = {tool.name for tool in await mcp.list_tools()}

    categories = {
        "metadata": sorted(registered & METADATA_TOOLS),
        "statistics": sorted(registered & STATISTICS_TOOLS),
        "processing": sorted(registered & PROCESSING_TOOLS),
    }

    return categories


@mcp.resource("gis://raster/formats")
def raster_formats() -> list[dict]:
    """Return raster formats supported by the GIS server."""

    return [
        {
            "name": "GeoTIFF",
            "extension": ".tif",
            "driver": "GTiff",
        },
        {
            "name": "Erdas Imagine",
            "extension": ".img",
            "driver": "HFA",
        },
        {
            "name": "NetCDF",
            "extension": ".nc",
            "driver": "netCDF",
        },
    ]
