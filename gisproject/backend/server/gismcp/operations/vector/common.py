import math
from pathlib import Path

import numpy as np
import pyogrio
import shapely
from pyogrio import raw as pyogrio_raw
from shapely import wkt, to_wkt
from shapely.ops import transform
from pyproj import CRS, Transformer

WKT_PRECISION_DEGREES = 6
WKT_PRECISION_METERS = 3


def dump_wkt(geometry, crs: str | None = None) -> str:
    precision = WKT_PRECISION_DEGREES

    if crs is not None:
        try:
            unit_name = CRS.from_user_input(crs).axis_info[0].unit_name

            if unit_name != "degree":
                precision = WKT_PRECISION_METERS

        except Exception:
            pass

    return to_wkt(geometry, rounding_precision=precision, trim=True)


def load_geometry(wkt_geometry: str):
    try:
        geometry = wkt.loads(wkt_geometry)

    except Exception as exc:
        raise ValueError(
            f"Invalid WKT geometry: {exc}"
        ) from exc

    if geometry.is_empty:
        raise ValueError(
            "Geometry is empty."
        )

    if not geometry.is_valid:
        raise ValueError(
            "Geometry is invalid."
        )

    return geometry


def reproject(geometry, source_crs: str, target_crs: str):
    try:
        transformer = Transformer.from_crs(
            CRS.from_user_input(source_crs),
            CRS.from_user_input(target_crs),
            always_xy=True,
        )

        return transform(
            transformer.transform,
            geometry,
        )

    except Exception as exc:
        raise ValueError(
            f"Failed to reproject geometry from "
            f"'{source_crs}' to '{target_crs}': {exc}"
        ) from exc


def to_python(value):
    """Convert a numpy scalar from a feature attribute into a JSON-friendly value."""

    if value is None:
        return None

    if isinstance(value, np.datetime64):
        return None if np.isnat(value) else str(value)

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, float) and math.isnan(value):
        return None

    return value


def reproject_many(geometries, source_crs: str, target_crs: str):
    """Reproject an array of geometries with a single Transformer."""

    try:
        transformer = Transformer.from_crs(
            CRS.from_user_input(source_crs),
            CRS.from_user_input(target_crs),
            always_xy=True,
        )

        return shapely.transform(
            geometries,
            lambda coords: np.column_stack(
                transformer.transform(coords[:, 0], coords[:, 1])
            ),
        )

    except Exception as exc:
        raise ValueError(
            f"Failed to reproject geometries from "
            f"'{source_crs}' to '{target_crs}': {exc}"
        ) from exc


def check_vector_path(vector_path: str) -> None:
    if not Path(vector_path).exists():
        raise ValueError(
            f"Vector file not found: {vector_path}"
        )


def resolve_layer(vector_path: str, layer: str | None) -> str:
    """Return the requested layer name, defaulting to the first layer."""

    check_vector_path(vector_path)

    try:
        layers = [str(name) for name, _ in pyogrio.list_layers(vector_path)]

    except Exception as exc:
        raise ValueError(
            f"Failed to open vector '{vector_path}': {exc}"
        ) from exc

    if not layers:
        raise ValueError(
            f"Vector '{vector_path}' has no layers."
        )

    if layer is None:
        return layers[0]

    if layer not in layers:
        raise ValueError(
            f"Layer '{layer}' not found. Available layers: {layers}"
        )

    return layer


def layer_info(vector_path: str, layer: str | None) -> tuple[str, dict]:
    layer = resolve_layer(vector_path, layer)

    try:
        info = pyogrio.read_info(
            vector_path,
            layer=layer,
            force_feature_count=True,
            force_total_bounds=True,
        )

    except Exception as exc:
        raise ValueError(
            f"Failed to read layer '{layer}': {exc}"
        ) from exc

    return layer, info


def read_features(
    vector_path: str,
    layer: str,
    *,
    where: str | None = None,
    bbox: tuple[float, float, float, float] | None = None,
    max_features: int | None = None,
    read_geometry: bool = True,
):
    """Read features from a layer, returning (fids, geometries, fields, field_data)."""

    try:
        meta, fids, geometry, field_data = pyogrio_raw.read(
            vector_path,
            layer=layer,
            where=where,
            bbox=bbox,
            max_features=max_features,
            read_geometry=read_geometry,
            return_fids=True,
        )

    except Exception as exc:
        raise ValueError(
            f"Failed to read features from layer '{layer}': {exc}"
        ) from exc

    geometries = shapely.from_wkb(geometry) if read_geometry else None

    return fids, geometries, list(meta["fields"]), field_data


def feature_properties(fields, field_data, index: int) -> dict:
    return {
        str(name): to_python(column[index])
        for name, column in zip(fields, field_data)
    }
