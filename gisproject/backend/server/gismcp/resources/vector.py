from server.gismcp.server import mcp


SUPPORTED_CRS = [
    {
        "name": "WGS 84",
        "epsg": "EPSG:4326",
        "type": "geographic",
    },
    {
        "name": "WGS 84 / UTM zone 43N",
        "epsg": "EPSG:32643",
        "type": "projected",
    },
    {
        "name": "WGS 84 / UTM zone 44N",
        "epsg": "EPSG:32644",
        "type": "projected",
    },
    {
        "name": "WGS 84 / UTM zone 45N",
        "epsg": "EPSG:32645",
        "type": "projected",
    },
]


@mcp.resource("gis://vector/crs/supported")
def supported_crs() -> list[dict]:
    """Return CRS supported by the Vector GIS MCP server."""
    return SUPPORTED_CRS


GEOMETRY_TOOLS = {
    "calculate_area_tool",
    "calculate_length_tool",
    "calculate_centroid_tool",
    "buffer_geometry_tool",
    "intersection_tool",
    "difference_tool",
    "union_geometries_tool",
    "simplify_geometry_tool",
    "convex_hull_tool",
    "bounds_tool",
    "validate_geometry_tool",
}

PROJECTION_TOOLS = {
    "transform_geometry_tool",
    "get_crs_info_tool",
    "is_projected_crs_tool",
    "calculate_utm_zone_tool",
}


@mcp.resource("gis://vector/operations")
async def vector_operations() -> dict:
    """Return available vector GIS operations, grouped by category."""

    registered = {tool.name for tool in await mcp.list_tools()}

    categories = {
        "geometry": sorted(registered & GEOMETRY_TOOLS),
        "projection": sorted(registered & PROJECTION_TOOLS),
    }

    uncategorized = sorted(registered - GEOMETRY_TOOLS - PROJECTION_TOOLS)
    if uncategorized:
        categories["uncategorized"] = uncategorized

    return categories


@mcp.resource("gis://vector/formats")
def vector_formats() -> list[dict]:
    """Return vector formats supported by the GIS server."""

    return [
        {
            "name": "GeoJSON",
            "extension": ".geojson",
            "driver": "GeoJSON",
        },
        {
            "name": "ESRI Shapefile",
            "extension": ".shp",
            "driver": "ESRI Shapefile",
        },
        {
            "name": "GeoPackage",
            "extension": ".gpkg",
            "driver": "GPKG",
        },
    ]