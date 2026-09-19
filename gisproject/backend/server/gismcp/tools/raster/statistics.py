from server.gismcp.operations.raster.statistics import (
    calculate_raster_statistics,
    calculate_percentiles,
    get_unique_values,
    calculate_histogram,
    get_pixel_value,
    calculate_nodata_percentage,
)
from server.gismcp.schemas.raster.statistics import (
    CalculateRasterStatisticsInput,
    CalculateRasterStatisticsOutput,
    CalculatePercentilesInput,
    CalculatePercentilesOutput,
    GetUniqueValuesInput,
    GetUniqueValuesOutput,
    CalculateHistogramInput,
    CalculateHistogramOutput,
    GetPixelValueInput,
    GetPixelValueOutput,
    CalculateNodataPercentageInput,
    CalculateNodataPercentageOutput,
)
from server.gismcp.server import mcp


@mcp.tool(title="calculate_raster_statistics_tool")
def calculate_raster_statistics_tool(
    payload: CalculateRasterStatisticsInput,
) -> CalculateRasterStatisticsOutput:
    """Calculate min, max, mean, standard deviation and sum of valid pixels in a raster band."""

    return calculate_raster_statistics(payload)


@mcp.tool(title="calculate_percentiles_tool")
def calculate_percentiles_tool(
    payload: CalculatePercentilesInput,
) -> CalculatePercentilesOutput:
    """Calculate percentiles of the valid pixel values in a raster band."""

    return calculate_percentiles(payload)


@mcp.tool(title="get_unique_values_tool")
def get_unique_values_tool(
    payload: GetUniqueValuesInput,
) -> GetUniqueValuesOutput:
    """Get the unique pixel values of a raster band with their pixel counts, e.g. for classified rasters."""

    return get_unique_values(payload)


@mcp.tool(title="calculate_histogram_tool")
def calculate_histogram_tool(
    payload: CalculateHistogramInput,
) -> CalculateHistogramOutput:
    """Calculate an equal-width histogram of the valid pixel values in a raster band."""

    return calculate_histogram(payload)


@mcp.tool(title="get_pixel_value_tool")
def get_pixel_value_tool(
    payload: GetPixelValueInput,
) -> GetPixelValueOutput:
    """Get the pixel value of a raster band at an x/y location."""

    return get_pixel_value(payload)


@mcp.tool(title="calculate_nodata_percentage_tool")
def calculate_nodata_percentage_tool(
    payload: CalculateNodataPercentageInput,
) -> CalculateNodataPercentageOutput:
    """Calculate the percentage of NoData pixels in a raster band."""

    return calculate_nodata_percentage(payload)
