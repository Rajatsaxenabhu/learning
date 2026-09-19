from pydantic import BaseModel, Field


class GetRasterMetadataInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/dem.tif."
    )


class GetRasterMetadataOutput(BaseModel):
    driver: str = Field(
        description="GDAL driver used to read the raster, e.g. GTiff."
    )

    width: int = Field(
        description="Number of pixel columns."
    )

    height: int = Field(
        description="Number of pixel rows."
    )

    band_count: int = Field(
        description="Number of bands in the raster."
    )

    dtypes: list[str] = Field(
        description="Data type of each band, in band order."
    )

    crs: str | None = Field(
        description="CRS of the raster, e.g. EPSG:32644. Null if the raster has no CRS."
    )

    bounds: list[float] = Field(
        description="Raster extent as [min_x, min_y, max_x, max_y] in the raster CRS."
    )

    resolution: list[float] = Field(
        description="Pixel size as [x_resolution, y_resolution] in CRS units."
    )

    nodata: float | None = Field(
        description="NoData value of the first band. Null if not defined."
    )

    transform: list[float] = Field(
        description="Affine transform coefficients [a, b, c, d, e, f]."
    )


class GetRasterCrsInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/dem.tif."
    )


class GetRasterCrsOutput(BaseModel):
    crs: str | None = Field(
        description="CRS of the raster, e.g. EPSG:32644. Null if the raster has no CRS."
    )

    name: str | None = Field(
        description="Human-readable name of the CRS. Null if the raster has no CRS."
    )

    epsg_code: int | None = Field(
        description="EPSG code of the CRS. Null if it cannot be matched to an EPSG code."
    )

    is_projected: bool | None = Field(
        description="True if the CRS is projected (planar), false if geographic. Null if the raster has no CRS."
    )

    axis_units: str | None = Field(
        description="Unit of the CRS axes, e.g. 'metre' or 'degree'. Null if the raster has no CRS."
    )


class GetRasterBoundsInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/dem.tif."
    )


class GetRasterBoundsOutput(BaseModel):
    min_x: float = Field(description="Minimum X (west) coordinate.")

    min_y: float = Field(description="Minimum Y (south) coordinate.")

    max_x: float = Field(description="Maximum X (east) coordinate.")

    max_y: float = Field(description="Maximum Y (north) coordinate.")

    crs: str | None = Field(
        description="CRS the bounds are expressed in. Null if the raster has no CRS."
    )


class GetRasterResolutionInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/dem.tif."
    )


class GetRasterResolutionOutput(BaseModel):
    x_resolution: float = Field(
        description="Pixel width in CRS units."
    )

    y_resolution: float = Field(
        description="Pixel height in CRS units (absolute value)."
    )

    units: str | None = Field(
        description="Unit of the resolution, e.g. 'metre' or 'degree'. Null if the raster has no CRS."
    )


class GetRasterBandInfoInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/dem.tif."
    )


class RasterBandInfo(BaseModel):
    band: int = Field(
        description="1-based band index."
    )

    dtype: str = Field(
        description="Data type of the band, e.g. float32."
    )

    nodata: float | None = Field(
        description="NoData value of the band. Null if not defined."
    )

    description: str | None = Field(
        description="Band description, if the file provides one."
    )

    color_interpretation: str = Field(
        description="Color interpretation of the band, e.g. gray, red, undefined."
    )


class GetRasterBandInfoOutput(BaseModel):
    band_count: int = Field(
        description="Number of bands in the raster."
    )

    bands: list[RasterBandInfo] = Field(
        description="Information for each band, in band order."
    )
