
from server.gismcp.config.logging import logger
from server.gismcp.server import mcp
import server.gismcp.tools.vector
import server.gismcp.resources.vector

if __name__ == "__main__":
    logger.info("Starting GIS MCP server over stdio")
    mcp.run()
