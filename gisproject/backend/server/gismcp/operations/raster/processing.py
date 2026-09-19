from contextlib import ExitStack
from pathlib import Path

import numpy as np
import rasterio
import shapely
from pyogrio import raw as pyogrio_raw
from rasterio.crs import CRS as RioCRS
from rasterio.enums import Resampling
from rasterio.features import rasterize, shapes
from rasterio.mask import mask as rio_mask
from rasterio.merge import merge
from rasterio.transform import from_origin
from rasterio.warp import calculate_default_transform, reproject, transform_bounds
from rasterio.windows import Window, from_bounds
from shapely.geometry import mapping, shape

from server.gismcp.operations.raster.common import (
    open_raster,
    read_band,
    crs_string,
    default_nodata,
    prepare_output,
    write_raster,
    describe_output,
    require_crs,
)
from server.gismcp.operations.vector.common import (
    load_geometry,
    reproject as reproject_geometry,
    layer_info,
    read_features,
)
from server.gismcp.schemas.raster.processing import (
    ClipRasterInput,
    ClipRasterOutput,
    MaskRasterInput,
    MaskRasterOutput,
    ReprojectRasterInput,
    ReprojectRasterOutput,
    ResampleRasterInput,
    ResampleRasterOutput,
    MergeRastersInput,
    MergeRastersOutput,
    CropRasterInput,
    CropRasterOutput,
    RasterizeVectorInput,
    RasterizeVectorOutput,
    PolygonizeRasterInput,
    PolygonizeRasterOutput,
)

MAX_RASTERIZE_PIXELS = 200_000_000

POLYGON_DRIVERS = {
    ".gpkg": "GPKG",
    ".geojson": "GeoJSON",
    ".shp": "ESRI Shapefile",
}

SHAPES_DTYPES = {"uint8", "uint16", "int16", "int32", "float32"}


def _nodata_for(dataset) -> float | int:
    return dataset.nodata if dataset.nodata is not None else default_nodata(dataset.dtypes[0])


def _mask_raster(payload, *, crop: bool, invert: bool):
    output = prepare_output(payload.output_path, payload.overwrite, [payload.raster_path])

    with open_raster(payload.raster_path) as dataset:
        raster_crs = require_crs(dataset)

        geometry = reproject_geometry(
            load_geometry(payload.wkt_geometry),
            payload.crs,
            raster_crs,
        )

        nodata = _nodata_for(dataset)

        try:
            data, transform = rio_mask(
                dataset,
                [mapping(geometry)],
                crop=crop,
                invert=invert,
                nodata=nodata,
                all_touched=payload.all_touched,
            )

        except ValueError as exc:
            raise ValueError(
                f"Failed to mask raster: {exc}"
            ) from exc

        write_raster(
            output,
            data,
            crs=dataset.crs,
            transform=transform,
            nodata=nodata,
        )

    return describe_output(output)


def clip_raster(
    payload: ClipRasterInput,
) -> ClipRasterOutput:

    return ClipRasterOutput(**_mask_raster(payload, crop=True, invert=False))


def mask_raster(
    payload: MaskRasterInput,
) -> MaskRasterOutput:

    return MaskRasterOutput(**_mask_raster(payload, crop=False, invert=payload.invert))


def reproject_raster(
    payload: ReprojectRasterInput,
) -> ReprojectRasterOutput:

    output = prepare_output(payload.output_path, payload.overwrite, [payload.raster_path])

    try:
        target_crs = RioCRS.from_user_input(payload.target_crs)

    except Exception as exc:
        raise ValueError(
            f"Invalid CRS '{payload.target_crs}': {exc}"
        ) from exc

    with open_raster(payload.raster_path) as dataset:
        require_crs(dataset)

        try:
            transform, width, height = calculate_default_transform(
                dataset.crs,
                target_crs,
                dataset.width,
                dataset.height,
                *dataset.bounds,
                resolution=payload.resolution,
            )

            nodata = _nodata_for(dataset)

            destination = np.full(
                (dataset.count, height, width),
                nodata,
                dtype=dataset.dtypes[0],
            )

            reproject(
                source=rasterio.band(dataset, list(range(1, dataset.count + 1))),
                destination=destination,
                dst_transform=transform,
                dst_crs=target_crs,
                src_nodata=dataset.nodata,
                dst_nodata=nodata,
                resampling=Resampling[payload.resampling],
            )

        except Exception as exc:
            raise ValueError(
                f"Failed to reproject raster to '{payload.target_crs}': {exc}"
            ) from exc

        write_raster(
            output,
            destination,
            crs=target_crs,
            transform=transform,
            nodata=nodata,
        )

    return ReprojectRasterOutput(**describe_output(output))


def resample_raster(
    payload: ResampleRasterInput,
) -> ResampleRasterOutput:

    output = prepare_output(payload.output_path, payload.overwrite, [payload.raster_path])

    with open_raster(payload.raster_path) as dataset:
        x_res, y_res = dataset.res

        width = max(1, round(dataset.width * x_res / payload.resolution))
        height = max(1, round(dataset.height * y_res / payload.resolution))

        try:
            data = dataset.read(
                out_shape=(dataset.count, height, width),
                resampling=Resampling[payload.resampling],
            )

        except Exception as exc:
            raise ValueError(
                f"Failed to resample raster: {exc}"
            ) from exc

        transform = dataset.transform * dataset.transform.scale(
            dataset.width / width,
            dataset.height / height,
        )

        write_raster(
            output,
            data,
            crs=dataset.crs,
            transform=transform,
            nodata=dataset.nodata,
        )

    return ResampleRasterOutput(**describe_output(output))


def merge_rasters(
    payload: MergeRastersInput,
) -> MergeRastersOutput:

    output = prepare_output(payload.output_path, payload.overwrite, payload.raster_paths)

    with ExitStack() as stack:
        datasets = [
            stack.enter_context(open_raster(path))
            for path in payload.raster_paths
        ]

        first = datasets[0]

        for path, dataset in zip(payload.raster_paths, datasets):
            if dataset.crs != first.crs:
                raise ValueError(
                    f"Raster '{path}' has a different CRS from '{payload.raster_paths[0]}'."
                )

            if dataset.count != first.count:
                raise ValueError(
                    f"Raster '{path}' has {dataset.count} band(s), "
                    f"expected {first.count}."
                )

        nodata = _nodata_for(first)

        try:
            data, transform = merge(
                datasets,
                method=payload.method,
                nodata=nodata,
            )

        except Exception as exc:
            raise ValueError(
                f"Failed to merge rasters: {exc}"
            ) from exc

        write_raster(
            output,
            data,
            crs=first.crs,
            transform=transform,
            nodata=nodata,
        )

    return MergeRastersOutput(
        **describe_output(output),
        merged_count=len(payload.raster_paths),
    )


def crop_raster(
    payload: CropRasterInput,
) -> CropRasterOutput:

    output = prepare_output(payload.output_path, payload.overwrite, [payload.raster_path])

    with open_raster(payload.raster_path) as dataset:
        raster_crs = require_crs(dataset)

        bounds = payload.bounds

        if payload.crs is not None:
            try:
                bounds = transform_bounds(
                    RioCRS.from_user_input(payload.crs),
                    dataset.crs,
                    *bounds,
                )

            except Exception as exc:
                raise ValueError(
                    f"Failed to transform crop box from '{payload.crs}' to raster CRS: {exc}"
                ) from exc

        window = from_bounds(*bounds, transform=dataset.transform)
        window = Window(
            int(np.floor(window.col_off)),
            int(np.floor(window.row_off)),
            int(np.ceil(window.width)),
            int(np.ceil(window.height)),
        )

        try:
            window = window.intersection(Window(0, 0, dataset.width, dataset.height))

        except Exception as exc:
            raise ValueError(
                "Crop box does not overlap the raster."
            ) from exc

        if window.width < 1 or window.height < 1:
            raise ValueError(
                "Crop box does not overlap the raster."
            )

        write_raster(
            output,
            dataset.read(window=window),
            crs=dataset.crs,
            transform=dataset.window_transform(window),
            nodata=dataset.nodata,
        )

    return CropRasterOutput(**describe_output(output))


def rasterize_vector(
    payload: RasterizeVectorInput,
) -> RasterizeVectorOutput:

    output = prepare_output(payload.output_path, payload.overwrite, [payload.vector_path])

    layer, info = layer_info(payload.vector_path, payload.layer)

    if info.get("total_bounds") is None or int(info["features"]) == 0:
        raise ValueError(
            f"Layer '{layer}' has no features."
        )

    if payload.attribute is not None and payload.attribute not in info["fields"]:
        raise ValueError(
            f"Attribute '{payload.attribute}' not found. "
            f"Available fields: {list(info['fields'])}"
        )

    minx, miny, maxx, maxy = info["total_bounds"]

    width = max(1, int(np.ceil((maxx - minx) / payload.resolution)))
    height = max(1, int(np.ceil((maxy - miny) / payload.resolution)))

    if width * height > MAX_RASTERIZE_PIXELS:
        raise ValueError(
            f"Output would be {width}x{height} pixels. "
            f"Use a coarser resolution (limit is {MAX_RASTERIZE_PIXELS} pixels)."
        )

    _, geometries, fields, field_data = read_features(
        payload.vector_path,
        layer,
    )

    if payload.attribute is None:
        values = np.full(len(geometries), payload.burn_value)

    else:
        try:
            values = np.asarray(
                field_data[fields.index(payload.attribute)],
                dtype="float64",
            )

        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Attribute '{payload.attribute}' is not numeric."
            ) from exc

    usable = [
        (mapping(geometry), float(value))
        for geometry, value in zip(geometries, values)
        if geometry is not None and not geometry.is_empty and np.isfinite(value)
    ]

    if not usable:
        raise ValueError(
            "No features with a geometry and a valid value to burn."
        )

    transform = from_origin(minx, maxy, payload.resolution, payload.resolution)

    try:
        data = rasterize(
            usable,
            out_shape=(height, width),
            transform=transform,
            fill=payload.fill_value,
            all_touched=payload.all_touched,
            dtype="float32",
        )

    except Exception as exc:
        raise ValueError(
            f"Failed to rasterize layer '{layer}': {exc}"
        ) from exc

    write_raster(
        output,
        data[np.newaxis, :, :],
        crs=info.get("crs"),
        transform=transform,
        nodata=None,
    )

    return RasterizeVectorOutput(
        **describe_output(output),
        features_burned=len(usable),
    )


def polygonize_raster(
    payload: PolygonizeRasterInput,
) -> PolygonizeRasterOutput:

    driver = POLYGON_DRIVERS.get(Path(payload.output_path).suffix.lower())

    if driver is None:
        raise ValueError(
            f"Unsupported output extension. Use one of: {sorted(POLYGON_DRIVERS)}"
        )

    output = prepare_output(payload.output_path, payload.overwrite, [payload.raster_path])

    with open_raster(payload.raster_path) as dataset:
        data = read_band(dataset, payload.band)
        valid = ~np.ma.getmaskarray(data)

        if not valid.any():
            raise ValueError(
                f"Band {payload.band} has no valid pixels."
            )

        array = data.filled(0)

        if array.dtype.name not in SHAPES_DTYPES:
            array = array.astype("float32")

        polygons = []
        values = []

        try:
            for geometry, value in shapes(
                array,
                mask=valid,
                transform=dataset.transform,
                connectivity=payload.connectivity,
            ):
                polygons.append(shape(geometry))
                values.append(value)

        except Exception as exc:
            raise ValueError(
                f"Failed to polygonize band {payload.band}: {exc}"
            ) from exc

        crs = crs_string(dataset)

    if output.exists():
        output.unlink()

    try:
        pyogrio_raw.write(
            str(output),
            geometry=shapely.to_wkb(np.array(polygons, dtype=object)),
            field_data=[np.array(values, dtype="float64")],
            fields=["value"],
            crs=crs,
            driver=driver,
            geometry_type="Polygon",
        )

    except Exception as exc:
        raise ValueError(
            f"Failed to write polygons to '{payload.output_path}': {exc}"
        ) from exc

    return PolygonizeRasterOutput(
        output_path=str(output),
        driver=driver,
        polygon_count=len(polygons),
        crs=crs,
        value_field="value",
    )
