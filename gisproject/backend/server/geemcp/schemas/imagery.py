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
