from mcp.server import MCPServer
from shapely import wkt
from shapely.ops import transform
from pyproj import CRS, Transformer
from enum import Enum
from pydantic import BaseModel

mcp=MCPServer("gis_agent")



class EPSGCode(Enum):
    WGS84 = "EPSG:4326"
    UTM_ZONE_44N = "EPSG:32644"
    UTM_ZONE_43N = "EPSG:32643"
    UTM_ZONE_45N = "EPSG:32645"


class area_schame(BaseModel):
    wkt_geometry:str
    crs:str

@mcp.resource("gisprojection://available")
def get_projection()->list[str]:
    """get the avaibale projection """
    return [projection.value for projection in EPSGCode]

@mcp.tool()
def calculate_area(payload:area_schame)->float:
    """calculate the area"""
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

    return projected_geometry.area


if __name__ == "__main__":
    mcp.run(transport="streamable-http")