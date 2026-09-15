import logging

from mcp.server import MCPServer
from shapely import wkt
from shapely.ops import transform
from pyproj import CRS, Transformer
from enum import Enum
from pydantic import BaseModel
from config.logging import logger


mcp = MCPServer("gis_agent")


class EPSGCode(Enum):
    WGS84 = "EPSG:4326"
    UTM_ZONE_44N = "EPSG:32644"
    UTM_ZONE_43N = "EPSG:32643"
    UTM_ZONE_45N = "EPSG:32645"


class AreaSchema(BaseModel):
    wkt_geometry: str
    crs: str


@mcp.resource("gisprojection://available")
def get_projection() -> list[str]:
    """Get available projections."""
    return [projection.value for projection in EPSGCode]


@mcp.tool()
def calculate_area(payload: AreaSchema) -> float:
    """Calculate the area."""

    logger.info(
        "Calculating area with CRS=%s",
        payload.crs,
    )

    geometry = wkt.loads(payload.wkt_geometry)

    source_crs = payload.crs
    target_crs = EPSGCode.UTM_ZONE_44N

    transformer = Transformer.from_crs(
        CRS.from_user_input(source_crs),
        CRS.from_user_input(target_crs.value),
        always_xy=True,
    )

    projected_geometry = transform(
        transformer.transform,
        geometry,
    )

    area = projected_geometry.area

    logger.info("Calculated area=%s", area)

    return area


if __name__ == "__main__":
    logger.info("Starting GIS MCP server over stdio")
    mcp.run()