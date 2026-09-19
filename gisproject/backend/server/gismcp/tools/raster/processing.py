from server.gismcp.operations.raster.processing import (
    clip_raster,
    mask_raster,
    reproject_raster,
    resample_raster,
    merge_rasters,
    crop_raster,
    rasterize_vector,
    polygonize_raster,
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
from server.gismcp.server import WRITE, mcp


@mcp.tool(title="clip_raster_tool", annotations=WRITE)
def clip_raster_tool(
    payload: ClipRasterInput,
) -> ClipRasterOutput:
    """Clip a raster to a polygon: crops to its extent and sets pixels outside it to NoData. Writes a new GeoTIFF."""

    return clip_raster(payload)


@mcp.tool(title="mask_raster_tool", annotations=WRITE)
def mask_raster_tool(
    payload: MaskRasterInput,
) -> MaskRasterOutput:
    """Set raster pixels outside (or inside, if inverted) a polygon to NoData, keeping the full extent. Writes a new GeoTIFF."""

    return mask_raster(payload)


@mcp.tool(title="reproject_raster_tool", annotations=WRITE)
def reproject_raster_tool(
    payload: ReprojectRasterInput,
) -> ReprojectRasterOutput:
    """Reproject a raster into another CRS. Writes a new GeoTIFF."""

    return reproject_raster(payload)


@mcp.tool(title="resample_raster_tool", annotations=WRITE)
def resample_raster_tool(
    payload: ResampleRasterInput,
) -> ResampleRasterOutput:
    """Change the pixel size of a raster while keeping its CRS and extent. Writes a new GeoTIFF."""

    return resample_raster(payload)


@mcp.tool(title="merge_rasters_tool", annotations=WRITE)
def merge_rasters_tool(
    payload: MergeRastersInput,
) -> MergeRastersOutput:
    """Mosaic two or more rasters with the same CRS into one raster. Writes a new GeoTIFF."""

    return merge_rasters(payload)


@mcp.tool(title="crop_raster_tool", annotations=WRITE)
def crop_raster_tool(
    payload: CropRasterInput,
) -> CropRasterOutput:
    """Crop a raster to a bounding box without masking any pixels. Writes a new GeoTIFF."""

    return crop_raster(payload)


@mcp.tool(title="rasterize_vector_tool", annotations=WRITE)
def rasterize_vector_tool(
    payload: RasterizeVectorInput,
) -> RasterizeVectorOutput:
    """Burn the features of a vector layer into a new single-band GeoTIFF, by constant value or numeric attribute."""

    return rasterize_vector(payload)


@mcp.tool(title="polygonize_raster_tool", annotations=WRITE)
def polygonize_raster_tool(
    payload: PolygonizeRasterInput,
) -> PolygonizeRasterOutput:
    """Convert groups of equal-valued raster pixels into polygons with a 'value' attribute. Writes a vector file."""

    return polygonize_raster(payload)
