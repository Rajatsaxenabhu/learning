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
