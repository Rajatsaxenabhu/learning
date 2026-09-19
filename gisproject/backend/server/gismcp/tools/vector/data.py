from server.gismcp.operations.vector.data import (
    get_vector_metadata,
    list_vector_layers,
    get_vector_schema,
    get_feature_count,
    filter_features,
    spatial_query,
    features_within_distance,
)
from server.gismcp.schemas.vector.data import (
    GetVectorMetadataInput,
    GetVectorMetadataOutput,
    ListVectorLayersInput,
    ListVectorLayersOutput,
    GetVectorSchemaInput,
    GetVectorSchemaOutput,
    GetFeatureCountInput,
    GetFeatureCountOutput,
    FilterFeaturesInput,
    FilterFeaturesOutput,
    SpatialQueryInput,
    SpatialQueryOutput,
    FeaturesWithinDistanceInput,
    FeaturesWithinDistanceOutput,
)
from server.gismcp.server import READ_ONLY, mcp


@mcp.tool(title="get_vector_metadata_tool", annotations=READ_ONLY)
def get_vector_metadata_tool(
    payload: GetVectorMetadataInput,
) -> GetVectorMetadataOutput:
    """Get general metadata of a vector layer: driver, CRS, geometry type, feature count and bounds."""

    return get_vector_metadata(payload)


@mcp.tool(title="list_vector_layers_tool", annotations=READ_ONLY)
def list_vector_layers_tool(
    payload: ListVectorLayersInput,
) -> ListVectorLayersOutput:
    """List the layers in a vector file with their geometry types."""

    return list_vector_layers(payload)


@mcp.tool(title="get_vector_schema_tool", annotations=READ_ONLY)
def get_vector_schema_tool(
    payload: GetVectorSchemaInput,
) -> GetVectorSchemaOutput:
    """Get the attribute fields and geometry type of a vector layer."""

    return get_vector_schema(payload)


@mcp.tool(title="get_feature_count_tool", annotations=READ_ONLY)
def get_feature_count_tool(
    payload: GetFeatureCountInput,
) -> GetFeatureCountOutput:
    """Count the features in a vector layer, optionally matching an attribute filter."""

    return get_feature_count(payload)


@mcp.tool(title="filter_features_tool", annotations=READ_ONLY)
def filter_features_tool(
    payload: FilterFeaturesInput,
) -> FilterFeaturesOutput:
    """Select features from a vector layer with an attribute (OGR SQL WHERE) filter."""

    return filter_features(payload)


@mcp.tool(title="spatial_query_tool", annotations=READ_ONLY)
def spatial_query_tool(
    payload: SpatialQueryInput,
) -> SpatialQueryOutput:
    """Select features from a vector layer that satisfy a spatial predicate against a geometry."""

    return spatial_query(payload)


@mcp.tool(title="features_within_distance_tool", annotations=READ_ONLY)
def features_within_distance_tool(
    payload: FeaturesWithinDistanceInput,
) -> FeaturesWithinDistanceOutput:
    """Find features in a vector layer within a distance in meters of a geometry, nearest first."""

    return features_within_distance(payload)
