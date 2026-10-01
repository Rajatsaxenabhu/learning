import ee

from server.geemcp.config.gee import initialize_gee
from server.geemcp.operations.imagery import (
    search_satellite_images,
)
from server.geemcp.schemas.imagery import (
    SatelliteSearchRequest,
    BoundingBox,
)


initialize_gee()

request = SatelliteSearchRequest(
    bbox=BoundingBox(
        min_lon=82.90,
        min_lat=25.20,
        max_lon=83.10,
        max_lat=25.40,
    ),
    start_date="2026-06-01",
    end_date="2026-06-30",
    max_cloud_percentage=20,
    limit=5,
)

result = search_satellite_images(request)

print(result)
