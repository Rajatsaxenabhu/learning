from operations.vector.projection import (
    transform_geometry,
    get_crs_info,
    is_projected_crs,
    calculate_utm_zone,
)
from schemas.vector.projection import (
    TransformGeometryInput,
    TransformGeometryOutput,
    GetCrsInfoInput,
    GetCrsInfoOutput,
    IsProjectedCrsInput,
    IsProjectedCrsOutput,
    CalculateUtmZoneInput,
    CalculateUtmZoneOutput,
)
from server import mcp


@mcp.tool(title="transform_geometry_tool")
def transform_geometry_tool(
    payload: TransformGeometryInput,
) -> TransformGeometryOutput:
    """Transform a vector geometry from one CRS to another."""

    return transform_geometry(payload)


@mcp.tool(title="get_crs_info_tool")
def get_crs_info_tool(
    payload: GetCrsInfoInput,
) -> GetCrsInfoOutput:
    """Get descriptive information about a coordinate reference system."""

    return get_crs_info(payload)


@mcp.tool(title="is_projected_crs_tool")
def is_projected_crs_tool(
    payload: IsProjectedCrsInput,
) -> IsProjectedCrsOutput:
    """Check whether a coordinate reference system is projected (planar) or geographic."""

    return is_projected_crs(payload)


@mcp.tool(title="calculate_utm_zone_tool")
def calculate_utm_zone_tool(
    payload: CalculateUtmZoneInput,
) -> CalculateUtmZoneOutput:
    """Calculate the UTM zone and recommended EPSG code for a vector geometry."""

    return calculate_utm_zone(payload)
