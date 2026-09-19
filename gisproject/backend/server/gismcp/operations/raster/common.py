from contextlib import contextmanager
from pathlib import Path

import numpy as np
import rasterio
from pyproj import CRS


@contextmanager
def open_raster(raster_path: str):
    path = Path(raster_path)

    if not path.is_file():
        raise ValueError(
            f"Raster file not found: {raster_path}"
        )

    try:
        dataset = rasterio.open(path)

    except Exception as exc:
        raise ValueError(
            f"Failed to open raster '{raster_path}': {exc}"
        ) from exc

    try:
        yield dataset

    finally:
        dataset.close()


def validate_band(dataset, band: int) -> None:
    if band < 1 or band > dataset.count:
        raise ValueError(
            f"Band {band} is out of range. "
            f"Raster has {dataset.count} band(s)."
        )


def read_band(dataset, band: int):
    """Read a band as a masked array, masking NoData and non-finite values."""

    validate_band(dataset, band)

    try:
        data = dataset.read(band, masked=True)

    except Exception as exc:
        raise ValueError(
            f"Failed to read band {band}: {exc}"
        ) from exc

    if data.dtype.kind == "f":
        data = np.ma.masked_where(~np.isfinite(data.data), data)

    return data


def valid_values(dataset, band: int):
    """Return the 1-D array of valid pixel values, raising if there are none."""

    values = read_band(dataset, band).compressed()

    if values.size == 0:
        raise ValueError(
            f"Band {band} has no valid pixels."
        )

    return values


def crs_string(dataset) -> str | None:
    if dataset.crs is None:
        return None

    epsg = dataset.crs.to_epsg()

    return f"EPSG:{epsg}" if epsg else dataset.crs.to_string()


def crs_axis_unit(dataset) -> str | None:
    if dataset.crs is None:
        return None

    try:
        return CRS.from_user_input(dataset.crs.to_wkt()).axis_info[0].unit_name

    except Exception:
        return None
