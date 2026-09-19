import numpy as np
from pyproj import CRS, Transformer

from server.gismcp.operations.raster.common import (
    open_raster,
    read_band,
    valid_values,
    validate_band,
)
from server.gismcp.schemas.raster.statistics import (
    CalculateRasterStatisticsInput,
    CalculateRasterStatisticsOutput,
    CalculatePercentilesInput,
    CalculatePercentilesOutput,
    PercentileValue,
    GetUniqueValuesInput,
    GetUniqueValuesOutput,
    UniqueValueCount,
    CalculateHistogramInput,
    CalculateHistogramOutput,
    GetPixelValueInput,
    GetPixelValueOutput,
    CalculateNodataPercentageInput,
    CalculateNodataPercentageOutput,
)


def calculate_raster_statistics(
    payload: CalculateRasterStatisticsInput,
) -> CalculateRasterStatisticsOutput:

    with open_raster(payload.raster_path) as dataset:
        data = read_band(dataset, payload.band)
        values = data.compressed().astype("float64")

        if values.size == 0:
            raise ValueError(
                f"Band {payload.band} has no valid pixels."
            )

        return CalculateRasterStatisticsOutput(
            band=payload.band,
            min=float(values.min()),
            max=float(values.max()),
            mean=float(values.mean()),
            std=float(values.std()),
            sum=float(values.sum()),
            valid_pixel_count=int(values.size),
            total_pixel_count=int(data.size),
        )


def calculate_percentiles(
    payload: CalculatePercentilesInput,
) -> CalculatePercentilesOutput:

    invalid = [p for p in payload.percentiles if not 0 <= p <= 100]

    if invalid:
        raise ValueError(
            f"Percentiles must be between 0 and 100, got: {invalid}"
        )

    with open_raster(payload.raster_path) as dataset:
        values = valid_values(dataset, payload.band)

        results = np.percentile(values, payload.percentiles)

        return CalculatePercentilesOutput(
            band=payload.band,
            percentiles=[
                PercentileValue(percentile=p, value=float(v))
                for p, v in zip(payload.percentiles, results)
            ],
            valid_pixel_count=int(values.size),
        )


def get_unique_values(
    payload: GetUniqueValuesInput,
) -> GetUniqueValuesOutput:

    with open_raster(payload.raster_path) as dataset:
        values = valid_values(dataset, payload.band)

        unique, counts = np.unique(values, return_counts=True)

        limited = slice(0, payload.max_values)

        return GetUniqueValuesOutput(
            band=payload.band,
            values=[
                UniqueValueCount(value=float(v), count=int(c))
                for v, c in zip(unique[limited], counts[limited])
            ],
            total_unique=int(unique.size),
            truncated=bool(unique.size > payload.max_values),
        )


def calculate_histogram(
    payload: CalculateHistogramInput,
) -> CalculateHistogramOutput:

    with open_raster(payload.raster_path) as dataset:
        values = valid_values(dataset, payload.band)

        try:
            counts, bin_edges = np.histogram(values, bins=payload.bins)

        except Exception as exc:
            raise ValueError(
                f"Failed to compute histogram: {exc}"
            ) from exc

        return CalculateHistogramOutput(
            band=payload.band,
            bin_edges=[float(e) for e in bin_edges],
            counts=[int(c) for c in counts],
        )


def get_pixel_value(
    payload: GetPixelValueInput,
) -> GetPixelValueOutput:

    with open_raster(payload.raster_path) as dataset:
        validate_band(dataset, payload.band)

        x, y = payload.x, payload.y

        if payload.crs is not None:
            if dataset.crs is None:
                raise ValueError(
                    "Raster has no CRS, so coordinates cannot be transformed."
                )

            try:
                transformer = Transformer.from_crs(
                    CRS.from_user_input(payload.crs),
                    CRS.from_user_input(dataset.crs.to_wkt()),
                    always_xy=True,
                )
                x, y = transformer.transform(x, y)

            except Exception as exc:
                raise ValueError(
                    f"Failed to transform coordinates from "
                    f"'{payload.crs}' to the raster CRS: {exc}"
                ) from exc

        try:
            row, col = dataset.index(x, y)

        except Exception as exc:
            raise ValueError(
                f"Failed to locate pixel for ({payload.x}, {payload.y}): {exc}"
            ) from exc

        if not (0 <= row < dataset.height and 0 <= col < dataset.width):
            raise ValueError(
                f"Location ({payload.x}, {payload.y}) is outside the raster bounds."
            )

        window = ((row, row + 1), (col, col + 1))
        pixel = dataset.read(payload.band, window=window, masked=True)[0, 0]

        is_nodata = bool(
            pixel is np.ma.masked
            or (np.issubdtype(type(pixel), np.floating) and not np.isfinite(pixel))
        )

        return GetPixelValueOutput(
            band=payload.band,
            value=None if is_nodata else float(pixel),
            is_nodata=is_nodata,
            row=int(row),
            col=int(col),
        )


def calculate_nodata_percentage(
    payload: CalculateNodataPercentageInput,
) -> CalculateNodataPercentageOutput:

    with open_raster(payload.raster_path) as dataset:
        data = read_band(dataset, payload.band)

        total = int(data.size)
        nodata = total - int(data.count())

        return CalculateNodataPercentageOutput(
            band=payload.band,
            nodata_percentage=(nodata / total * 100) if total else 0.0,
            nodata_pixel_count=nodata,
            total_pixel_count=total,
        )
