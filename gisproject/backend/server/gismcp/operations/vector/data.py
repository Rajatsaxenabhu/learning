import numpy as np
import shapely

from server.gismcp.operations.vector.common import (
    load_geometry,
    reproject,
    reproject_many,
    dump_wkt,
    layer_info,
    read_features,
    feature_properties,
    resolve_layer,
)
from server.gismcp.operations.vector.geometry import TARGET_CRS
from server.gismcp.schemas.vector.data import (
    GetVectorMetadataInput,
    GetVectorMetadataOutput,
    ListVectorLayersInput,
    ListVectorLayersOutput,
    VectorLayerInfo,
    GetVectorSchemaInput,
    GetVectorSchemaOutput,
    VectorFieldInfo,
    GetFeatureCountInput,
    GetFeatureCountOutput,
    FilterFeaturesInput,
    FilterFeaturesOutput,
    FeatureRecord,
    SpatialQueryInput,
    SpatialQueryOutput,
    FeaturesWithinDistanceInput,
    FeaturesWithinDistanceOutput,
    NearbyFeatureRecord,
)

import pyogrio


def _layer_crs(info: dict, layer: str) -> str:
    if not info.get("crs"):
        raise ValueError(
            f"Layer '{layer}' has no CRS, so spatial queries are not possible."
        )

    return info["crs"]


def _geometry_wkt(geometry, crs: str, include_geometry: bool) -> str | None:
    if not include_geometry or geometry is None:
        return None

    return dump_wkt(geometry, crs)


def get_vector_metadata(
    payload: GetVectorMetadataInput,
) -> GetVectorMetadataOutput:

    layer, info = layer_info(payload.vector_path, payload.layer)

    bounds = info.get("total_bounds")

    return GetVectorMetadataOutput(
        driver=info["driver"],
        layer=layer,
        crs=info.get("crs"),
        geometry_type=info.get("geometry_type"),
        feature_count=int(info["features"]),
        bounds=None if bounds is None else [float(b) for b in bounds],
        field_count=len(info["fields"]),
    )


def list_vector_layers(
    payload: ListVectorLayersInput,
) -> ListVectorLayersOutput:

    resolve_layer(payload.vector_path, None)

    return ListVectorLayersOutput(
        layers=[
            VectorLayerInfo(
                name=str(name),
                geometry_type=None if geometry_type is None else str(geometry_type),
            )
            for name, geometry_type in pyogrio.list_layers(payload.vector_path)
        ]
    )


def get_vector_schema(
    payload: GetVectorSchemaInput,
) -> GetVectorSchemaOutput:

    layer, info = layer_info(payload.vector_path, payload.layer)

    return GetVectorSchemaOutput(
        layer=layer,
        geometry_type=info.get("geometry_type"),
        fields=[
            VectorFieldInfo(name=str(name), dtype=str(dtype))
            for name, dtype in zip(info["fields"], info["dtypes"])
        ],
    )


def get_feature_count(
    payload: GetFeatureCountInput,
) -> GetFeatureCountOutput:

    layer, info = layer_info(payload.vector_path, payload.layer)

    if payload.where is None:
        count = int(info["features"])

    else:
        fids, _, _, _ = read_features(
            payload.vector_path,
            layer,
            where=payload.where,
            read_geometry=False,
        )
        count = len(fids)

    return GetFeatureCountOutput(
        layer=layer,
        feature_count=count,
    )


def filter_features(
    payload: FilterFeaturesInput,
) -> FilterFeaturesOutput:

    layer, info = layer_info(payload.vector_path, payload.layer)

    fids, geometries, fields, field_data = read_features(
        payload.vector_path,
        layer,
        where=payload.where,
        max_features=payload.max_features + 1,
        read_geometry=payload.include_geometry,
    )

    truncated = len(fids) > payload.max_features
    count = min(len(fids), payload.max_features)

    return FilterFeaturesOutput(
        layer=layer,
        features=[
            FeatureRecord(
                fid=int(fids[i]),
                properties=feature_properties(fields, field_data, i),
                wkt_geometry=_geometry_wkt(
                    None if geometries is None else geometries[i],
                    info.get("crs"),
                    payload.include_geometry,
                ),
            )
            for i in range(count)
        ],
        returned_count=count,
        truncated=truncated,
    )


def spatial_query(
    payload: SpatialQueryInput,
) -> SpatialQueryOutput:

    layer, info = layer_info(payload.vector_path, payload.layer)
    layer_crs = _layer_crs(info, layer)

    query_geometry = reproject(
        load_geometry(payload.wkt_geometry),
        payload.crs,
        layer_crs,
    )

    fids, geometries, fields, field_data = read_features(
        payload.vector_path,
        layer,
        bbox=None if payload.predicate == "disjoint" else tuple(query_geometry.bounds),
    )

    try:
        mask = getattr(shapely, payload.predicate)(geometries, query_geometry)

    except Exception as exc:
        raise ValueError(
            f"Failed to evaluate '{payload.predicate}': {exc}"
        ) from exc

    matches = np.flatnonzero(mask)
    returned = matches[: payload.max_features]

    return SpatialQueryOutput(
        layer=layer,
        features=[
            FeatureRecord(
                fid=int(fids[i]),
                properties=feature_properties(fields, field_data, i),
                wkt_geometry=_geometry_wkt(
                    geometries[i], layer_crs, payload.include_geometry
                ),
            )
            for i in returned
        ],
        matched_count=int(matches.size),
        returned_count=int(returned.size),
        truncated=bool(matches.size > returned.size),
    )


def features_within_distance(
    payload: FeaturesWithinDistanceInput,
) -> FeaturesWithinDistanceOutput:

    layer, info = layer_info(payload.vector_path, payload.layer)
    layer_crs = _layer_crs(info, layer)

    query_geometry = reproject(
        load_geometry(payload.wkt_geometry),
        payload.crs,
        TARGET_CRS,
    )

    search_area = reproject(
        query_geometry.buffer(payload.distance_m),
        TARGET_CRS,
        layer_crs,
    )

    fids, geometries, fields, field_data = read_features(
        payload.vector_path,
        layer,
        bbox=tuple(search_area.bounds),
    )

    projected = reproject_many(geometries, layer_crs, TARGET_CRS)
    distances = shapely.distance(projected, query_geometry)

    matches = np.flatnonzero(distances <= payload.distance_m)
    matches = matches[np.argsort(distances[matches], kind="stable")]
    returned = matches[: payload.max_features]

    return FeaturesWithinDistanceOutput(
        layer=layer,
        features=[
            NearbyFeatureRecord(
                fid=int(fids[i]),
                properties=feature_properties(fields, field_data, i),
                wkt_geometry=_geometry_wkt(
                    geometries[i], layer_crs, payload.include_geometry
                ),
                distance_m=float(distances[i]),
            )
            for i in returned
        ],
        matched_count=int(matches.size),
        returned_count=int(returned.size),
        truncated=bool(matches.size > returned.size),
        calculation_crs=TARGET_CRS,
    )
