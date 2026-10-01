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
    """What the LLM sees."""

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
    """One layer for the map. Never shown to the LLM."""

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
