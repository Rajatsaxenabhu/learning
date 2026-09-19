from typing import Literal

from pydantic import BaseModel, Field

ResamplingMethod = Literal[
    "nearest",
    "bilinear",
    "cubic",
    "cubic_spline",
    "lanczos",
    "average",
    "mode",
    "max",
    "min",
    "med",
]


class RasterProcessingInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/dem.tif."
    )

    output_path: str = Field(
        description="Path of the GeoTIFF to write, e.g. /data/dem_clipped.tif."
    )

    overwrite: bool = Field(
        default=False,
        description="Replace the output file if it already exists.",
    )


class RasterProcessingOutput(BaseModel):
    output_path: str = Field(description="Path of the raster that was written.")

    width: int = Field(description="Width of the output in pixels.")

    height: int = Field(description="Height of the output in pixels.")

    band_count: int = Field(description="Number of bands in the output.")

    crs: str | None = Field(description="CRS of the output raster.")

    bounds: list[float] = Field(
        description="Bounding box [left, bottom, right, top] of the output in its CRS."
    )


class ClipRasterInput(RasterProcessingInput):
    wkt_geometry: str = Field(
        description="Clip polygon in WKT format."
    )

    crs: str = Field(
        description="CRS of the clip polygon, e.g. EPSG:4326. It is reprojected to the raster's CRS."
    )

    all_touched: bool = Field(
        default=False,
        description="Keep every pixel touched by the polygon, not only those whose center is inside.",
    )


class ClipRasterOutput(RasterProcessingOutput):
    pass


class MaskRasterInput(ClipRasterInput):
    invert: bool = Field(
        default=False,
        description="Mask out the pixels inside the polygon instead of outside it.",
    )


class MaskRasterOutput(RasterProcessingOutput):
    pass


class ReprojectRasterInput(RasterProcessingInput):
    target_crs: str = Field(
        description="CRS to reproject into, e.g. EPSG:32644."
    )

    resampling: ResamplingMethod = Field(
        default="nearest",
        description="Resampling method. Use nearest for classified data, bilinear or cubic for continuous data.",
    )

    resolution: float | None = Field(
        default=None,
        gt=0,
        description="Output pixel size in target CRS units. Defaults to an automatic value.",
    )


class ReprojectRasterOutput(RasterProcessingOutput):
    pass


class ResampleRasterInput(RasterProcessingInput):
    resolution: float = Field(
        gt=0,
        description="New square pixel size in the raster's CRS units.",
    )

    resampling: ResamplingMethod = Field(
        default="nearest",
        description="Resampling method. Use nearest for classified data, bilinear or cubic for continuous data.",
    )


class ResampleRasterOutput(RasterProcessingOutput):
    pass


class MergeRastersInput(BaseModel):
    raster_paths: list[str] = Field(
        min_length=2,
        description="Paths of the rasters to merge. They must share CRS and band count.",
    )

    output_path: str = Field(
        description="Path of the GeoTIFF to write, e.g. /data/mosaic.tif."
    )

    method: Literal["first", "last", "min", "max"] = Field(
        default="first",
        description="How overlapping pixels are resolved.",
    )

    overwrite: bool = Field(
        default=False,
        description="Replace the output file if it already exists.",
    )


class MergeRastersOutput(RasterProcessingOutput):
    merged_count: int = Field(description="Number of rasters that were merged.")


class CropRasterInput(RasterProcessingInput):
    bounds: list[float] = Field(
        min_length=4,
        max_length=4,
        description="Crop box [minx, miny, maxx, maxy].",
    )

    crs: str | None = Field(
        default=None,
        description="CRS of the crop box. Defaults to the raster's own CRS.",
    )


class CropRasterOutput(RasterProcessingOutput):
    pass


class RasterizeVectorInput(BaseModel):
    vector_path: str = Field(
        description="Path to a local vector file, e.g. /data/parcels.gpkg."
    )

    layer: str | None = Field(
        default=None,
        description="Layer name. Defaults to the first layer in the file.",
    )

    output_path: str = Field(
        description="Path of the GeoTIFF to write, e.g. /data/parcels.tif."
    )

    resolution: float = Field(
        gt=0,
        description="Square pixel size in the layer's CRS units.",
    )

    attribute: str | None = Field(
        default=None,
        description="Numeric attribute to burn into the raster. Defaults to burn_value.",
    )

    burn_value: float = Field(
        default=1.0,
        description="Value burned for every feature when no attribute is given.",
    )

    fill_value: float = Field(
        default=0.0,
        description="Value of pixels not covered by any feature.",
    )

    all_touched: bool = Field(
        default=False,
        description="Burn every pixel touched by a feature, not only those whose center is inside.",
    )

    overwrite: bool = Field(
        default=False,
        description="Replace the output file if it already exists.",
    )


class RasterizeVectorOutput(RasterProcessingOutput):
    features_burned: int = Field(description="Number of features burned into the raster.")


class PolygonizeRasterInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/landcover.tif."
    )

    band: int = Field(
        default=1,
        ge=1,
        description="1-based band index to polygonize.",
    )

    output_path: str = Field(
        description="Path of the vector file to write. Extension picks the format: .gpkg, .geojson or .shp."
    )

    connectivity: Literal[4, 8] = Field(
        default=4,
        description="Pixel connectivity used to group cells of equal value.",
    )

    overwrite: bool = Field(
        default=False,
        description="Replace the output file if it already exists.",
    )


class PolygonizeRasterOutput(BaseModel):
    output_path: str = Field(description="Path of the vector file that was written.")

    driver: str = Field(description="OGR driver used for the output.")

    polygon_count: int = Field(description="Number of polygons written.")

    crs: str | None = Field(description="CRS of the output polygons.")

    value_field: str = Field(
        description="Attribute field holding the pixel value of each polygon."
    )
