from pydantic import BaseModel, Field


class CalculateAreaInput(BaseModel):
    wkt_geometry: str = Field(
        description="Geometry in WKT format."
    )

    crs: str = Field(
        description="Source coordinate reference system, e.g. EPSG:4326."
    )


class CalculateAreaOutput(BaseModel):
    area_m2: float = Field(
        description="Calculated area in square meters."
    )

    source_crs: str = Field(
        description="CRS of the input geometry."
    )

    calculation_crs: str = Field(
        description="Projected CRS used to calculate the area."
    )


class CalculateLengthInput(BaseModel):
    wkt_geometry: str = Field(
        description="Geometry in WKT format."
    )

    crs: str = Field(
        description="Source coordinate reference system, e.g. EPSG:4326."
    )


class CalculateLengthOutput(BaseModel):
    length_m: float = Field(
        description="Calculated length in meters."
    )

    source_crs: str = Field(
        description="CRS of the input geometry."
    )

    calculation_crs: str = Field(
        description="Projected CRS used to calculate the length."
    )


class CalculateCentroidInput(BaseModel):
    wkt_geometry: str = Field(
        description="Geometry in WKT format."
    )

    crs: str = Field(
        description="Coordinate reference system of the geometry, e.g. EPSG:4326."
    )


class CalculateCentroidOutput(BaseModel):
    wkt_centroid: str = Field(
        description="Centroid point in WKT format."
    )

    crs: str = Field(
        description="CRS of the centroid, same as the input geometry."
    )


class BufferGeometryInput(BaseModel):
    wkt_geometry: str = Field(
        description="Geometry in WKT format."
    )

    crs: str = Field(
        description="Source coordinate reference system, e.g. EPSG:4326."
    )

    distance_m: float = Field(
        description="Buffer distance in meters. Negative values shrink the geometry."
    )


class BufferGeometryOutput(BaseModel):
    wkt_geometry: str = Field(
        description="Buffered geometry in WKT format, reprojected back to the source CRS."
    )

    crs: str = Field(
        description="CRS of the returned geometry, same as the input."
    )

    distance_m: float = Field(
        description="Buffer distance applied, in meters."
    )


class IntersectionInput(BaseModel):
    wkt_geometry_a: str = Field(
        description="First geometry in WKT format."
    )

    wkt_geometry_b: str = Field(
        description="Second geometry in WKT format."
    )

    crs: str = Field(
        description="Coordinate reference system shared by both geometries, e.g. EPSG:4326."
    )


class IntersectionOutput(BaseModel):
    wkt_geometry: str = Field(
        description="Intersection geometry in WKT format."
    )

    crs: str = Field(
        description="CRS of the returned geometry, same as the input."
    )

    is_empty: bool = Field(
        description="True if the geometries do not intersect."
    )


class DifferenceInput(BaseModel):
    wkt_geometry_a: str = Field(
        description="Geometry to subtract from, in WKT format."
    )

    wkt_geometry_b: str = Field(
        description="Geometry to subtract, in WKT format."
    )

    crs: str = Field(
        description="Coordinate reference system shared by both geometries, e.g. EPSG:4326."
    )


class DifferenceOutput(BaseModel):
    wkt_geometry: str = Field(
        description="Difference geometry (a minus b) in WKT format."
    )

    crs: str = Field(
        description="CRS of the returned geometry, same as the input."
    )

    is_empty: bool = Field(
        description="True if subtracting b from a removes all of a."
    )


class UnionGeometriesInput(BaseModel):
    wkt_geometries: list[str] = Field(
        description="Geometries to union, each in WKT format. Requires at least 2 entries."
    )

    crs: str = Field(
        description="Coordinate reference system shared by all geometries, e.g. EPSG:4326."
    )


class UnionGeometriesOutput(BaseModel):
    wkt_geometry: str = Field(
        description="Union geometry in WKT format."
    )

    crs: str = Field(
        description="CRS of the returned geometry, same as the input."
    )


class SimplifyGeometryInput(BaseModel):
    wkt_geometry: str = Field(
        description="Geometry in WKT format."
    )

    crs: str = Field(
        description="Source coordinate reference system, e.g. EPSG:4326."
    )

    tolerance_m: float = Field(
        description="Simplification tolerance in meters. Larger values remove more detail."
    )

    preserve_topology: bool = Field(
        default=True,
        description="If True, avoids simplifications that would make the geometry invalid.",
    )


class SimplifyGeometryOutput(BaseModel):
    wkt_geometry: str = Field(
        description="Simplified geometry in WKT format, reprojected back to the source CRS."
    )

    crs: str = Field(
        description="CRS of the returned geometry, same as the input."
    )

    tolerance_m: float = Field(
        description="Simplification tolerance applied, in meters."
    )


class ConvexHullInput(BaseModel):
    wkt_geometry: str = Field(
        description="Geometry in WKT format."
    )

    crs: str = Field(
        description="Coordinate reference system of the geometry, e.g. EPSG:4326."
    )


class ConvexHullOutput(BaseModel):
    wkt_geometry: str = Field(
        description="Convex hull geometry in WKT format."
    )

    crs: str = Field(
        description="CRS of the returned geometry, same as the input."
    )


class BoundsInput(BaseModel):
    wkt_geometry: str = Field(
        description="Geometry in WKT format."
    )

    crs: str = Field(
        description="Coordinate reference system of the geometry, e.g. EPSG:4326."
    )


class BoundsOutput(BaseModel):
    min_x: float = Field(
        description="Minimum X (or longitude) coordinate."
    )

    min_y: float = Field(
        description="Minimum Y (or latitude) coordinate."
    )

    max_x: float = Field(
        description="Maximum X (or longitude) coordinate."
    )

    max_y: float = Field(
        description="Maximum Y (or latitude) coordinate."
    )

    crs: str = Field(
        description="CRS of the returned bounds, same as the input."
    )


class ValidateGeometryInput(BaseModel):
    wkt_geometry: str = Field(
        description="Geometry in WKT format."
    )


class ValidateGeometryOutput(BaseModel):
    is_valid: bool = Field(
        description="True if the geometry is topologically valid."
    )

    is_empty: bool = Field(
        description="True if the geometry contains no coordinates."
    )

    reason: str = Field(
        description="Explanation of the validity result, e.g. the location of a self-intersection."
    )
