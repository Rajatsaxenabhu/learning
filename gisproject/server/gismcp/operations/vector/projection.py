import math

from pyproj import CRS

from operations.vector.common import load_geometry, reproject, dump_wkt
from schemas.vector.projection import (
    TransformGeometryInput,
    TransformGeometryOutput,
    GetCrsInfoInput,
    GetCrsInfoOutput,
    IsProjectedCrsInput,
    IsProjectedCrsOutput,
    CalculateUtmZoneInput,
    CalculateUtmZoneOutput,
)

WGS84_CRS = "EPSG:4326"


def transform_geometry(
    payload: TransformGeometryInput,
) -> TransformGeometryOutput:

    geometry = load_geometry(payload.wkt_geometry)

    result_geometry = reproject(
        geometry,
        payload.source_crs,
        payload.target_crs,
    )

    return TransformGeometryOutput(
        wkt_geometry=dump_wkt(result_geometry, payload.target_crs),
        source_crs=payload.source_crs,
        target_crs=payload.target_crs,
    )


def get_crs_info(
    payload: GetCrsInfoInput,
) -> GetCrsInfoOutput:

    try:
        crs = CRS.from_user_input(payload.crs)

    except Exception as exc:
        raise ValueError(
            f"Invalid CRS '{payload.crs}': {exc}"
        ) from exc

    return GetCrsInfoOutput(
        crs=payload.crs,
        name=crs.name,
        is_geographic=crs.is_geographic,
        is_projected=crs.is_projected,
        axis_units=crs.axis_info[0].unit_name,
    )


def is_projected_crs(
    payload: IsProjectedCrsInput,
) -> IsProjectedCrsOutput:

    try:
        crs = CRS.from_user_input(payload.crs)

    except Exception as exc:
        raise ValueError(
            f"Invalid CRS '{payload.crs}': {exc}"
        ) from exc

    return IsProjectedCrsOutput(
        crs=payload.crs,
        is_projected=crs.is_projected,
    )


def calculate_utm_zone(
    payload: CalculateUtmZoneInput,
) -> CalculateUtmZoneOutput:

    geometry = load_geometry(payload.wkt_geometry)

    geographic_geometry = reproject(
        geometry,
        payload.crs,
        WGS84_CRS,
    )

    longitude, latitude = (
        geographic_geometry.centroid.x,
        geographic_geometry.centroid.y,
    )

    zone_number = math.floor((longitude + 180) / 6) + 1
    hemisphere = "N" if latitude >= 0 else "S"

    epsg_base = 32600 if hemisphere == "N" else 32700
    epsg_code = f"EPSG:{epsg_base + zone_number}"

    return CalculateUtmZoneOutput(
        zone_number=zone_number,
        hemisphere=hemisphere,
        epsg_code=epsg_code,
    )
