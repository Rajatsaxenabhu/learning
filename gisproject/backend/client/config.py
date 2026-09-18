from dataclasses import dataclass
from typing import Any
from mcp import StdioServerParameters



@dataclass(frozen=True)
class MCPServerConfig:
    name: str
    transport: Any


GIS_STDIO_SERVER = MCPServerConfig(
    name="gis_local",
    transport=StdioServerParameters(
        command="uv",
        args=["run", "-m", "server.gismcp.stdiomain"],
    ),
)

GIS_SERVER = MCPServerConfig(
    name="gis",
    transport="http://localhost:8000/mcp",
)

GEE_SERVER = MCPServerConfig(
    name="gee",
    transport="http://localhost:8001/mcp",
)

POSTGIS_SERVER = MCPServerConfig(
    name="postgis",
    transport="http://localhost:8002/mcp",
)