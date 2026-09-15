from pydantic import BaseModel, Field


class TransformGeometryInput(BaseModel):
    wkt_geometry: str = Field(
        description="Geometry in WKT format."
    )

    source_crs: str = Field(
        description="CRS the geometry is currently in, e.g. EPSG:4326."
    )

    target_crs: str = Field(
        description="CRS to transform the geometry into, e.g. EPSG:32644."
    )


class TransformGeometryOutput(BaseModel):
    wkt_geometry: str = Field(
        description="Geometry in WKT format, expressed in the target CRS."
    )

    source_crs: str = Field(
        description="CRS the geometry was originally in."
    )

    target_crs: str = Field(
        description="CRS the returned geometry is expressed in."
    )


class GetCrsInfoInput(BaseModel):
    crs: str = Field(
        description="Coordinate reference system to describe, e.g. EPSG:4326."
    )


class GetCrsInfoOutput(BaseModel):
    crs: str = Field(
        description="CRS that was described, as given."
    )

    name: str = Field(
        description="Human-readable name of the CRS."
    )

    is_geographic: bool = Field(
        description="True if the CRS uses angular (lon/lat) coordinates."
    )

    is_projected: bool = Field(
        description="True if the CRS uses linear (planar) coordinates."
    )

    axis_units: str = Field(
        description="Unit of the CRS's coordinate axes, e.g. 'metre' or 'degree'."
    )


class IsProjectedCrsInput(BaseModel):
    crs: str = Field(
        description="Coordinate reference system to check, e.g. EPSG:4326."
    )


class IsProjectedCrsOutput(BaseModel):
    crs: str = Field(
        description="CRS that was checked, as given."
    )

    is_projected: bool = Field(
        description="True if the CRS uses linear (planar) coordinates rather than lon/lat."
    )


class CalculateUtmZoneInput(BaseModel):
    wkt_geometry: str = Field(
        description="Geometry in WKT format, used to locate the UTM zone via its centroid."
    )

    crs: str = Field(
        description="Coordinate reference system of the geometry, e.g. EPSG:4326."
    )


class CalculateUtmZoneOutput(BaseModel):
    zone_number: int = Field(
        description="UTM zone number (1-60) containing the geometry's centroid."
    )

    hemisphere: str = Field(
        description="'N' or 'S', the hemisphere of the geometry's centroid."
    )

    epsg_code: str = Field(
        description="Recommended UTM EPSG code for the geometry, e.g. EPSG:32644."
    )
