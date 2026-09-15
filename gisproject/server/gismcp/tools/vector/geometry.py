from operations.vector.geometry import (
    calculate_area,
    calculate_length,
    calculate_centroid,
    buffer_geometry,
    intersection,
    difference,
    union_geometries,
    simplify_geometry,
    convex_hull,
    bounds,
    validate_geometry,
)
from schemas.vector.geometry import (
    CalculateAreaInput,
    CalculateAreaOutput,
    CalculateLengthInput,
    CalculateLengthOutput,
    CalculateCentroidInput,
    CalculateCentroidOutput,
    BufferGeometryInput,
    BufferGeometryOutput,
    IntersectionInput,
    IntersectionOutput,
    DifferenceInput,
    DifferenceOutput,
    UnionGeometriesInput,
    UnionGeometriesOutput,
    SimplifyGeometryInput,
    SimplifyGeometryOutput,
    ConvexHullInput,
    ConvexHullOutput,
    BoundsInput,
    BoundsOutput,
    ValidateGeometryInput,
    ValidateGeometryOutput,
)
from server import mcp


@mcp.tool(title="calculate_area_tool")
def calculate_area_tool(
    payload: CalculateAreaInput,
) -> CalculateAreaOutput:
    """Calculate the area of a vector geometry in square meters."""

    return calculate_area(payload)


@mcp.tool(title="calculate_length_tool")
def calculate_length_tool(
    payload: CalculateLengthInput,
) -> CalculateLengthOutput:
    """Calculate the length/perimeter of a vector geometry in meters."""

    return calculate_length(payload)


@mcp.tool(title="calculate_centroid_tool")
def calculate_centroid_tool(
    payload: CalculateCentroidInput,
) -> CalculateCentroidOutput:
    """Calculate the centroid of a vector geometry."""

    return calculate_centroid(payload)


@mcp.tool(title="buffer_geometry_tool")
def buffer_geometry_tool(
    payload: BufferGeometryInput,
) -> BufferGeometryOutput:
    """Buffer a vector geometry by a distance in meters."""

    return buffer_geometry(payload)


@mcp.tool(title="intersection_tool")
def intersection_tool(
    payload: IntersectionInput,
) -> IntersectionOutput:
    """Calculate the intersection of two vector geometries."""

    return intersection(payload)


@mcp.tool(title="difference_tool")
def difference_tool(
    payload: DifferenceInput,
) -> DifferenceOutput:
    """Calculate the difference (a minus b) of two vector geometries."""

    return difference(payload)


@mcp.tool(title="union_geometries_tool")
def union_geometries_tool(
    payload: UnionGeometriesInput,
) -> UnionGeometriesOutput:
    """Calculate the union of two or more vector geometries."""

    return union_geometries(payload)


@mcp.tool(title="simplify_geometry_tool")
def simplify_geometry_tool(
    payload: SimplifyGeometryInput,
) -> SimplifyGeometryOutput:
    """Simplify a vector geometry, removing detail below a tolerance in meters."""

    return simplify_geometry(payload)


@mcp.tool(title="convex_hull_tool")
def convex_hull_tool(
    payload: ConvexHullInput,
) -> ConvexHullOutput:
    """Calculate the convex hull of a vector geometry."""

    return convex_hull(payload)


@mcp.tool(title="bounds_tool")
def bounds_tool(
    payload: BoundsInput,
) -> BoundsOutput:
    """Calculate the bounding box of a vector geometry."""

    return bounds(payload)


@mcp.tool(title="validate_geometry_tool")
def validate_geometry_tool(
    payload: ValidateGeometryInput,
) -> ValidateGeometryOutput:
    """Check whether a vector geometry is topologically valid."""

    return validate_geometry(payload)
