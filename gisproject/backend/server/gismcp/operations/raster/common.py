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


def default_nodata(dtype) -> float | int:
    """Pick a NoData value for a dtype that has none defined."""

    dtype = np.dtype(dtype)

    if dtype.kind == "f":
        return -9999.0

    info = np.iinfo(dtype)

    return int(info.min) if dtype.kind == "i" else int(info.max)


def prepare_output(
    output_path: str,
    overwrite: bool,
    sources: list[str] | None = None,
) -> Path:
    path = Path(output_path)

    if not path.parent.is_dir():
        raise ValueError(
            f"Output directory does not exist: {path.parent}"
        )

    resolved = path.resolve()

    for source in sources or []:
        if Path(source).resolve() == resolved:
            raise ValueError(
                "Output path must differ from the input path."
            )

    if path.exists() and not overwrite:
        raise ValueError(
            f"Output file already exists: {output_path}. Set overwrite=true to replace it."
        )

    return path


def write_raster(path: Path, array, *, crs, transform, nodata) -> None:
    """Write a (bands, height, width) array to a compressed GeoTIFF."""

    count, height, width = array.shape

    try:
        with rasterio.open(
            path,
            "w",
            driver="GTiff",
            width=width,
            height=height,
            count=count,
            dtype=array.dtype,
            crs=crs,
            transform=transform,
            nodata=nodata,
            compress="lzw",
        ) as dst:
            dst.write(array)

    except Exception as exc:
        raise ValueError(
            f"Failed to write raster '{path}': {exc}"
        ) from exc


def describe_output(path: Path) -> dict:
    with open_raster(str(path)) as dataset:
        return {
            "output_path": str(path),
            "width": dataset.width,
            "height": dataset.height,
            "band_count": dataset.count,
            "crs": crs_string(dataset),
            "bounds": list(dataset.bounds),
        }


def require_crs(dataset) -> str:
    if dataset.crs is None:
        raise ValueError(
            "Raster has no CRS, so this operation is not possible."
        )

    return dataset.crs.to_wkt()
