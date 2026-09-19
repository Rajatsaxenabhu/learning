from pydantic import BaseModel, Field


class CalculateRasterStatisticsInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/dem.tif."
    )

    band: int = Field(
        default=1,
        ge=1,
        description="1-based band index to analyse.",
    )


class CalculateRasterStatisticsOutput(BaseModel):
    band: int = Field(description="Band that was analysed.")

    min: float = Field(description="Minimum valid pixel value.")

    max: float = Field(description="Maximum valid pixel value.")

    mean: float = Field(description="Mean of valid pixel values.")

    std: float = Field(description="Standard deviation of valid pixel values.")

    sum: float = Field(description="Sum of valid pixel values.")

    valid_pixel_count: int = Field(
        description="Number of pixels that are not NoData."
    )

    total_pixel_count: int = Field(
        description="Total number of pixels in the band."
    )


class CalculatePercentilesInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/dem.tif."
    )

    band: int = Field(
        default=1,
        ge=1,
        description="1-based band index to analyse.",
    )

    percentiles: list[float] = Field(
        default=[25.0, 50.0, 75.0],
        min_length=1,
        description="Percentiles to compute, each between 0 and 100.",
    )


class PercentileValue(BaseModel):
    percentile: float = Field(description="Requested percentile (0-100).")

    value: float = Field(description="Pixel value at that percentile.")


class CalculatePercentilesOutput(BaseModel):
    band: int = Field(description="Band that was analysed.")

    percentiles: list[PercentileValue] = Field(
        description="Computed value for each requested percentile."
    )

    valid_pixel_count: int = Field(
        description="Number of valid (non-NoData) pixels used."
    )


class GetUniqueValuesInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/landcover.tif."
    )

    band: int = Field(
        default=1,
        ge=1,
        description="1-based band index to analyse.",
    )

    max_values: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of unique values to return, lowest values first.",
    )


class UniqueValueCount(BaseModel):
    value: float = Field(description="Unique pixel value.")

    count: int = Field(description="Number of pixels with this value.")


class GetUniqueValuesOutput(BaseModel):
    band: int = Field(description="Band that was analysed.")

    values: list[UniqueValueCount] = Field(
        description="Unique values with pixel counts, sorted ascending."
    )

    total_unique: int = Field(
        description="Total number of unique valid values in the band."
    )

    truncated: bool = Field(
        description="True if total_unique exceeds max_values and the list was cut off."
    )


class CalculateHistogramInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/dem.tif."
    )

    band: int = Field(
        default=1,
        ge=1,
        description="1-based band index to analyse.",
    )

    bins: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Number of equal-width histogram bins.",
    )


class CalculateHistogramOutput(BaseModel):
    band: int = Field(description="Band that was analysed.")

    bin_edges: list[float] = Field(
        description="Bin edges; contains one more element than counts."
    )

    counts: list[int] = Field(
        description="Number of valid pixels in each bin."
    )


class GetPixelValueInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/dem.tif."
    )

    x: float = Field(
        description="X coordinate (longitude or easting) of the location."
    )

    y: float = Field(
        description="Y coordinate (latitude or northing) of the location."
    )

    crs: str | None = Field(
        default=None,
        description="CRS of the x/y coordinates, e.g. EPSG:4326. Defaults to the raster CRS.",
    )

    band: int = Field(
        default=1,
        ge=1,
        description="1-based band index to read.",
    )


class GetPixelValueOutput(BaseModel):
    band: int = Field(description="Band that was read.")

    value: float | None = Field(
        description="Pixel value at the location. Null if the pixel is NoData."
    )

    is_nodata: bool = Field(
        description="True if the pixel at the location is NoData."
    )

    row: int = Field(description="Pixel row index of the location.")

    col: int = Field(description="Pixel column index of the location.")


class CalculateNodataPercentageInput(BaseModel):
    raster_path: str = Field(
        description="Path to a local raster file, e.g. /data/dem.tif."
    )

    band: int = Field(
        default=1,
        ge=1,
        description="1-based band index to analyse.",
    )


class CalculateNodataPercentageOutput(BaseModel):
    band: int = Field(description="Band that was analysed.")

    nodata_percentage: float = Field(
        description="Percentage of pixels that are NoData (0-100)."
    )

    nodata_pixel_count: int = Field(
        description="Number of NoData pixels."
    )

    total_pixel_count: int = Field(
        description="Total number of pixels in the band."
    )
