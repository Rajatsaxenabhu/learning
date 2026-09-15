from shapely import wkt
from shapely.ops import transform
from pyproj import CRS, Transformer


def load_geometry(wkt_geometry: str):
    geometry = wkt.loads(wkt_geometry)

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
    transformer = Transformer.from_crs(
        CRS.from_user_input(source_crs),
        CRS.from_user_input(target_crs),
        always_xy=True,
    )

    return transform(
        transformer.transform,
        geometry,
    )
