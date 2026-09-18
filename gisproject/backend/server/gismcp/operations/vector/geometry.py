from shapely.ops import unary_union
from shapely.validation import explain_validity
from shapely import wkt

from server.gismcp.operations.vector.common import load_geometry, reproject, dump_wkt
from server.gismcp.schemas.vector.geometry import (
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

TARGET_CRS = "EPSG:32644"


def calculate_area(
    payload: CalculateAreaInput,
) -> CalculateAreaOutput:

    geometry = load_geometry(payload.wkt_geometry)

    projected_geometry = reproject(
        geometry,
        payload.crs,
        TARGET_CRS,
    )

    return CalculateAreaOutput(
        area_m2=projected_geometry.area,
        source_crs=payload.crs,
        calculation_crs=TARGET_CRS,
    )


def calculate_length(
    payload: CalculateLengthInput,
) -> CalculateLengthOutput:

    geometry = load_geometry(payload.wkt_geometry)

    projected_geometry = reproject(
        geometry,
        payload.crs,
        TARGET_CRS,
    )

    return CalculateLengthOutput(
        length_m=projected_geometry.length,
        source_crs=payload.crs,
        calculation_crs=TARGET_CRS,
    )


def calculate_centroid(
    payload: CalculateCentroidInput,
) -> CalculateCentroidOutput:

    geometry = load_geometry(payload.wkt_geometry)

    return CalculateCentroidOutput(
        wkt_centroid=dump_wkt(geometry.centroid, payload.crs),
        crs=payload.crs,
    )


def buffer_geometry(
    payload: BufferGeometryInput,
) -> BufferGeometryOutput:

    geometry = load_geometry(payload.wkt_geometry)

    projected_geometry = reproject(
        geometry,
        payload.crs,
        TARGET_CRS,
    )

    try:
        buffered_geometry = projected_geometry.buffer(
            payload.distance_m
        )

    except Exception as exc:
        raise ValueError(
            f"Failed to buffer geometry: {exc}"
        ) from exc

    result_geometry = reproject(
        buffered_geometry,
        TARGET_CRS,
        payload.crs,
    )

    return BufferGeometryOutput(
        wkt_geometry=dump_wkt(result_geometry, payload.crs),
        crs=payload.crs,
        distance_m=payload.distance_m,
    )


def intersection(
    payload: IntersectionInput,
) -> IntersectionOutput:

    geometry_a = load_geometry(payload.wkt_geometry_a)
    geometry_b = load_geometry(payload.wkt_geometry_b)

    try:
        result_geometry = geometry_a.intersection(geometry_b)

    except Exception as exc:
        raise ValueError(
            f"Failed to compute intersection: {exc}"
        ) from exc

    return IntersectionOutput(
        wkt_geometry=dump_wkt(result_geometry, payload.crs),
        crs=payload.crs,
        is_empty=result_geometry.is_empty,
    )


def difference(
    payload: DifferenceInput,
) -> DifferenceOutput:

    geometry_a = load_geometry(payload.wkt_geometry_a)
    geometry_b = load_geometry(payload.wkt_geometry_b)

    try:
        result_geometry = geometry_a.difference(geometry_b)

    except Exception as exc:
        raise ValueError(
            f"Failed to compute difference: {exc}"
        ) from exc

    return DifferenceOutput(
        wkt_geometry=dump_wkt(result_geometry, payload.crs),
        crs=payload.crs,
        is_empty=result_geometry.is_empty,
    )


def union_geometries(
    payload: UnionGeometriesInput,
) -> UnionGeometriesOutput:

    if len(payload.wkt_geometries) < 2:
        raise ValueError(
            "At least 2 geometries are required to compute a union."
        )

    geometries = [
        load_geometry(wkt_geometry)
        for wkt_geometry in payload.wkt_geometries
    ]

    try:
        result_geometry = unary_union(geometries)

    except Exception as exc:
        raise ValueError(
            f"Failed to compute union: {exc}"
        ) from exc

    return UnionGeometriesOutput(
        wkt_geometry=dump_wkt(result_geometry, payload.crs),
        crs=payload.crs,
    )


def simplify_geometry(
    payload: SimplifyGeometryInput,
) -> SimplifyGeometryOutput:

    geometry = load_geometry(payload.wkt_geometry)

    projected_geometry = reproject(
        geometry,
        payload.crs,
        TARGET_CRS,
    )

    try:
        simplified_geometry = projected_geometry.simplify(
            payload.tolerance_m,
            preserve_topology=payload.preserve_topology,
        )

    except Exception as exc:
        raise ValueError(
            f"Failed to simplify geometry: {exc}"
        ) from exc

    result_geometry = reproject(
        simplified_geometry,
        TARGET_CRS,
        payload.crs,
    )

    return SimplifyGeometryOutput(
        wkt_geometry=dump_wkt(result_geometry, payload.crs),
        crs=payload.crs,
        tolerance_m=payload.tolerance_m,
    )


def convex_hull(
    payload: ConvexHullInput,
) -> ConvexHullOutput:

    geometry = load_geometry(payload.wkt_geometry)

    return ConvexHullOutput(
        wkt_geometry=dump_wkt(geometry.convex_hull, payload.crs),
        crs=payload.crs,
    )


def bounds(
    payload: BoundsInput,
) -> BoundsOutput:

    geometry = load_geometry(payload.wkt_geometry)

    min_x, min_y, max_x, max_y = geometry.bounds

    return BoundsOutput(
        min_x=min_x,
        min_y=min_y,
        max_x=max_x,
        max_y=max_y,
        crs=payload.crs,
    )


def validate_geometry(
    payload: ValidateGeometryInput,
) -> ValidateGeometryOutput:

    try:
        geometry = wkt.loads(payload.wkt_geometry)

    except Exception as exc:
        return ValidateGeometryOutput(
            is_valid=False,
            is_empty=False,
            reason=f"Invalid WKT geometry: {exc}",
        )

    is_valid = geometry.is_valid

    return ValidateGeometryOutput(
        is_valid=is_valid,
        is_empty=geometry.is_empty,
        reason="Valid Geometry" if is_valid else explain_validity(geometry),
    )
