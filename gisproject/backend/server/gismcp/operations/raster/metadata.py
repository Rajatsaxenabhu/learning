from pyproj import CRS

from server.gismcp.operations.raster.common import (
    open_raster,
    crs_string,
    crs_axis_unit,
)
from server.gismcp.schemas.raster.metadata import (
    GetRasterMetadataInput,
    GetRasterMetadataOutput,
    GetRasterCrsInput,
    GetRasterCrsOutput,
    GetRasterBoundsInput,
    GetRasterBoundsOutput,
    GetRasterResolutionInput,
    GetRasterResolutionOutput,
    GetRasterBandInfoInput,
    GetRasterBandInfoOutput,
    RasterBandInfo,
)


def get_raster_metadata(
    payload: GetRasterMetadataInput,
) -> GetRasterMetadataOutput:

    with open_raster(payload.raster_path) as dataset:
        x_res, y_res = dataset.res

        return GetRasterMetadataOutput(
            driver=dataset.driver,
            width=dataset.width,
            height=dataset.height,
            band_count=dataset.count,
            dtypes=list(dataset.dtypes),
            crs=crs_string(dataset),
            bounds=list(dataset.bounds),
            resolution=[x_res, y_res],
            nodata=dataset.nodata,
            transform=list(dataset.transform)[:6],
        )


def get_raster_crs(
    payload: GetRasterCrsInput,
) -> GetRasterCrsOutput:

    with open_raster(payload.raster_path) as dataset:
        if dataset.crs is None:
            return GetRasterCrsOutput(
                crs=None,
                name=None,
                epsg_code=None,
                is_projected=None,
                axis_units=None,
            )

        try:
            crs = CRS.from_user_input(dataset.crs.to_wkt())

        except Exception as exc:
            raise ValueError(
                f"Failed to parse raster CRS: {exc}"
            ) from exc

        return GetRasterCrsOutput(
            crs=crs_string(dataset),
            name=crs.name,
            epsg_code=dataset.crs.to_epsg(),
            is_projected=crs.is_projected,
            axis_units=crs_axis_unit(dataset),
        )


def get_raster_bounds(
    payload: GetRasterBoundsInput,
) -> GetRasterBoundsOutput:

    with open_raster(payload.raster_path) as dataset:
        bounds = dataset.bounds

        return GetRasterBoundsOutput(
            min_x=bounds.left,
            min_y=bounds.bottom,
            max_x=bounds.right,
            max_y=bounds.top,
            crs=crs_string(dataset),
        )


def get_raster_resolution(
    payload: GetRasterResolutionInput,
) -> GetRasterResolutionOutput:

    with open_raster(payload.raster_path) as dataset:
        x_res, y_res = dataset.res

        return GetRasterResolutionOutput(
            x_resolution=x_res,
            y_resolution=abs(y_res),
            units=crs_axis_unit(dataset),
        )


def get_raster_band_info(
    payload: GetRasterBandInfoInput,
) -> GetRasterBandInfoOutput:

    with open_raster(payload.raster_path) as dataset:
        bands = [
            RasterBandInfo(
                band=index,
                dtype=dataset.dtypes[index - 1],
                nodata=dataset.nodatavals[index - 1],
                description=dataset.descriptions[index - 1],
                color_interpretation=dataset.colorinterp[index - 1].name.lower(),
            )
            for index in dataset.indexes
        ]

        return GetRasterBandInfoOutput(
            band_count=dataset.count,
            bands=bands,
        )
