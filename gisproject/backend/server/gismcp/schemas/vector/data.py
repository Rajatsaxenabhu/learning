from typing import Any, Literal

from pydantic import BaseModel, Field

SpatialPredicate = Literal[
    "intersects",
    "contains",
    "within",
    "touches",
    "crosses",
    "overlaps",
    "disjoint",
    "covers",
    "covered_by",
]


class VectorPathInput(BaseModel):
    vector_path: str = Field(
        description="Path to a local vector file, e.g. /data/parcels.gpkg."
    )

    layer: str | None = Field(
        default=None,
        description="Layer name. Defaults to the first layer in the file.",
    )


class FeatureRecord(BaseModel):
    fid: int = Field(description="Feature ID within the layer.")

    properties: dict[str, Any] = Field(
        description="Attribute values of the feature, keyed by field name."
    )

    wkt_geometry: str | None = Field(
        default=None,
        description="Feature geometry in WKT format, in the layer's CRS. Omitted if not requested.",
    )


class GetVectorMetadataInput(VectorPathInput):
    pass


class GetVectorMetadataOutput(BaseModel):
    driver: str = Field(description="OGR driver of the file, e.g. GPKG.")

    layer: str = Field(description="Layer that was described.")

    crs: str | None = Field(description="CRS of the layer, or null if undefined.")

    geometry_type: str | None = Field(description="Geometry type of the layer, e.g. Polygon.")

    feature_count: int = Field(description="Number of features in the layer.")

    bounds: list[float] | None = Field(
        description="Bounding box [minx, miny, maxx, maxy] in the layer's CRS, or null if empty."
    )

    field_count: int = Field(description="Number of attribute fields.")


class ListVectorLayersInput(BaseModel):
    vector_path: str = Field(
        description="Path to a local vector file, e.g. /data/parcels.gpkg."
    )


class VectorLayerInfo(BaseModel):
    name: str = Field(description="Layer name.")

    geometry_type: str | None = Field(description="Geometry type of the layer.")


class ListVectorLayersOutput(BaseModel):
    layers: list[VectorLayerInfo] = Field(description="Layers in the file.")


class GetVectorSchemaInput(VectorPathInput):
    pass


class VectorFieldInfo(BaseModel):
    name: str = Field(description="Attribute field name.")

    dtype: str = Field(description="Field data type, e.g. int64, float64, object.")


class GetVectorSchemaOutput(BaseModel):
    layer: str = Field(description="Layer that was described.")

    geometry_type: str | None = Field(description="Geometry type of the layer.")

    fields: list[VectorFieldInfo] = Field(description="Attribute fields of the layer.")


class GetFeatureCountInput(VectorPathInput):
    where: str | None = Field(
        default=None,
        description="Optional OGR SQL WHERE clause, e.g. \"population > 1000\".",
    )


class GetFeatureCountOutput(BaseModel):
    layer: str = Field(description="Layer that was counted.")

    feature_count: int = Field(description="Number of features (matching the filter, if any).")


class FilterFeaturesInput(VectorPathInput):
    where: str = Field(
        description="OGR SQL WHERE clause on attribute fields, e.g. \"name = 'Delhi' AND pop > 1000\"."
    )

    max_features: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of features to return.",
    )

    include_geometry: bool = Field(
        default=True,
        description="Whether to include each feature's geometry as WKT.",
    )


class FilterFeaturesOutput(BaseModel):
    layer: str = Field(description="Layer that was filtered.")

    features: list[FeatureRecord] = Field(description="Matching features.")

    returned_count: int = Field(description="Number of features returned.")

    truncated: bool = Field(
        description="True if more features matched than max_features."
    )


class SpatialQueryInput(VectorPathInput):
    wkt_geometry: str = Field(
        description="Query geometry in WKT format."
    )

    crs: str = Field(
        description="CRS of the query geometry, e.g. EPSG:4326. It is reprojected to the layer's CRS."
    )

    predicate: SpatialPredicate = Field(
        default="intersects",
        description="Spatial relation evaluated as <feature> <predicate> <query geometry>.",
    )

    max_features: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of features to return.",
    )

    include_geometry: bool = Field(
        default=True,
        description="Whether to include each feature's geometry as WKT.",
    )


class SpatialQueryOutput(BaseModel):
    layer: str = Field(description="Layer that was queried.")

    features: list[FeatureRecord] = Field(description="Features satisfying the predicate.")

    matched_count: int = Field(description="Total number of matching features.")

    returned_count: int = Field(description="Number of features returned.")

    truncated: bool = Field(
        description="True if more features matched than max_features."
    )


class FeaturesWithinDistanceInput(VectorPathInput):
    wkt_geometry: str = Field(
        description="Reference geometry in WKT format."
    )

    crs: str = Field(
        description="CRS of the reference geometry, e.g. EPSG:4326."
    )

    distance_m: float = Field(
        gt=0,
        description="Search distance in meters.",
    )

    max_features: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of features to return, nearest first.",
    )

    include_geometry: bool = Field(
        default=True,
        description="Whether to include each feature's geometry as WKT.",
    )


class NearbyFeatureRecord(FeatureRecord):
    distance_m: float = Field(
        description="Distance from the reference geometry in meters."
    )


class FeaturesWithinDistanceOutput(BaseModel):
    layer: str = Field(description="Layer that was searched.")

    features: list[NearbyFeatureRecord] = Field(
        description="Features within the distance, nearest first."
    )

    matched_count: int = Field(description="Total number of features within the distance.")

    returned_count: int = Field(description="Number of features returned.")

    truncated: bool = Field(
        description="True if more features matched than max_features."
    )

    calculation_crs: str = Field(
        description="Projected CRS in which distances were measured."
    )
