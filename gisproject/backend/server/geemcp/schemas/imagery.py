from typing import Literal

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):

    min_lon: float = Field(
        description="Minimum longitude."
    )

    min_lat: float = Field(
        description="Minimum latitude."
    )

    max_lon: float = Field(
        description="Maximum longitude."
    )

    max_lat: float = Field(
        description="Maximum latitude."
    )


class SatelliteSearchRequest(BaseModel):

    collection: str = Field(
        default="COPERNICUS/S2_SR_HARMONIZED",
        description=(
            "Google Earth Engine image collection ID. "
            "For Sentinel-2 use COPERNICUS/S2_SR_HARMONIZED "
            "(COPERNICUS/S2_SR is deprecated)."
        )
    )

    bbox: BoundingBox = Field(
        description="Bounding box in WGS84 longitude/latitude."
    )

    start_date: str = Field(
        description="Start date in YYYY-MM-DD format."
    )

    end_date: str = Field(
        description="End date in YYYY-MM-DD format."
    )

    max_cloud_percentage: float = Field(
        default=20.0,
        ge=0,
        le=100,
        description="Maximum allowed cloud percentage."
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of images to return."
    )


class ImageSummary(BaseModel):

    id: str = Field(description="Earth Engine image ID.")

    date: str | None = Field(description="Acquisition date, YYYY-MM-DD.")

    cloud_percentage: float | None = Field(
        description="Cloud cover percentage."
    )


class SatelliteSearchSummary(BaseModel):
    collection: str

    count: int = Field(
        description="Total images matching the search."
    )

    images: list[ImageSummary]

    shown_on_map: str | None = Field(
        default=None,
        description="ID of the image displayed on the map, if any.",
    )


class MapLayer(BaseModel):
    id: str

    type: Literal["geojson", "xyz"]

    name: str

    geojson: dict | None = Field(
        default=None,
        description="GeoJSON geometry, for type 'geojson'.",
    )

    url: str | None = Field(
        default=None,
        description="Tile URL template with {x}/{y}/{z}, for type 'xyz'.",
    )


class MapPayload(BaseModel):

    layers: list[MapLayer]

    extent: list[float] | None = Field(
        default=None,
        description="[min_lon, min_lat, max_lon, max_lat] in EPSG:4326.",
    )


class SatelliteSearchResult(BaseModel):

    summary: SatelliteSearchSummary

    map: MapPayload


class PropertyFilter(BaseModel):

    name: str = Field(
        description="Image property name, e.g. MGRS_TILE or SPACECRAFT_NAME."
    )

    operator: Literal[
        "eq", "neq", "gt", "gte", "lt", "lte", "contains"
    ] = Field(
        default="eq",
        description="Comparison operator.",
    )

    value: str = Field(
        description="Value to compare with. Numbers are parsed automatically."
    )


class FilterCollectionRequest(BaseModel):

    collection: str = Field(
        description="Google Earth Engine image collection ID."
    )

    bbox: BoundingBox | None = Field(
        default=None,
        description="Optional bounding box in WGS84 longitude/latitude.",
    )

    start_date: str | None = Field(
        default=None,
        description="Start date in YYYY-MM-DD format. Needs end_date.",
    )

    end_date: str | None = Field(
        default=None,
        description="End date in YYYY-MM-DD format. Needs start_date.",
    )

    max_cloud_percentage: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Maximum allowed cloud percentage.",
    )

    property_filters: list[PropertyFilter] = Field(
        default_factory=list,
        description="Extra filters on image properties.",
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of images to return.",
    )


class ImageRequest(BaseModel):

    image_id: str = Field(
        description=(
            "Full Earth Engine image ID, e.g. "
            "COPERNICUS/S2_SR_HARMONIZED/20250608T045721_20250608T050640_T44RPP."
        )
    )


class CollectionRequest(BaseModel):

    collection: str = Field(
        description="Google Earth Engine image collection ID."
    )


class ImageMetadata(BaseModel):

    id: str

    date: str | None

    cloud_percentage: float | None

    crs: str | None = Field(
        description="Coordinate reference system of the image."
    )

    bounds: list[float] | None = Field(
        description="[min_lon, min_lat, max_lon, max_lat]."
    )

    band_count: int

    properties: dict = Field(
        description="Selected image properties."
    )


class ImageMetadataResult(BaseModel):

    summary: ImageMetadata

    map: MapPayload


class BandInfo(BaseModel):

    name: str

    data_type: str

    scale_m: float | None = Field(
        description="Pixel size in metres, when the CRS is projected."
    )

    wavelength_nm: float | None = Field(
        description="Central wavelength in nanometres, when known."
    )


class ImageBandsResult(BaseModel):

    image_id: str

    bands: list[BandInfo]


class CollectionInfo(BaseModel):

    collection: str

    image_count: int

    start_date: str | None

    end_date: str | None

    bands: list[str]

    properties: list[str] = Field(
        description="Property names usable in filters."
    )

    cloud_property: str | None = Field(
        description="Property holding the cloud percentage, if known."
    )

    preview_supported: bool = Field(
        description="Whether a true-colour preview is available."
    )


class CompositeRequest(BaseModel):

    collection: str = Field(
        default="COPERNICUS/S2_SR_HARMONIZED",
        description="Google Earth Engine image collection ID.",
    )

    bbox: BoundingBox = Field(
        description="Bounding box in WGS84 longitude/latitude."
    )

    start_date: str = Field(
        description="Start date in YYYY-MM-DD format."
    )

    end_date: str = Field(
        description="End date in YYYY-MM-DD format."
    )

    method: Literal[
        "median", "mean", "mosaic", "min", "max"
    ] = Field(
        default="median",
        description="How to combine the images.",
    )

    max_cloud_percentage: float | None = Field(
        default=20.0,
        ge=0,
        le=100,
        description="Maximum allowed cloud percentage per image.",
    )

    bands: list[str] | None = Field(
        default=None,
        description="Three band names for the display. Defaults to true colour.",
    )

    min: float | None = Field(
        default=None,
        description="Display minimum. Defaults to the collection's true-colour value.",
    )

    max: float | None = Field(
        default=None,
        description="Display maximum. Defaults to the collection's true-colour value.",
    )


class CompositeSummary(BaseModel):

    collection: str

    method: str

    image_count: int = Field(
        description="Number of images combined."
    )

    start_date: str

    end_date: str

    bands: list[str]


class CompositeResult(BaseModel):

    summary: CompositeSummary

    map: MapPayload


class SpectralIndexRequest(BaseModel):

    index: Literal[
        "NDVI", "NDWI", "NDBI", "EVI", "SAVI", "NDMI", "NBR"
    ] = Field(
        description="Spectral index to calculate."
    )

    collection: str = Field(
        default="COPERNICUS/S2_SR_HARMONIZED",
        description="Sentinel-2 or Landsat 8/9 Level-2 collection ID.",
    )

    bbox: BoundingBox = Field(
        description="Bounding box in WGS84 longitude/latitude."
    )

    start_date: str = Field(
        description="Start date in YYYY-MM-DD format."
    )

    end_date: str = Field(
        description="End date in YYYY-MM-DD format."
    )

    method: Literal[
        "median", "mean", "mosaic", "min", "max"
    ] = Field(
        default="median",
        description="How to combine the images before calculating.",
    )

    max_cloud_percentage: float | None = Field(
        default=20.0,
        ge=0,
        le=100,
        description="Maximum allowed cloud percentage per image.",
    )


class IndexStats(BaseModel):

    mean: float | None

    min: float | None

    max: float | None

    std: float | None


class SpectralIndexSummary(BaseModel):

    index: str

    formula: str

    collection: str

    method: str

    image_count: int

    start_date: str

    end_date: str

    pixel_size_m: int = Field(
        description="Pixel size used for the statistics."
    )

    stats: IndexStats


class SpectralIndexResult(BaseModel):

    summary: SpectralIndexSummary

    map: MapPayload
