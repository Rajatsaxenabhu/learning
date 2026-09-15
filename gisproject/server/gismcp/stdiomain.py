
from config.logging import logger
from server import mcp
import tools.vector
import resources.vector

if __name__ == "__main__":
    logger.info("Starting GIS MCP server over stdio")
    mcp.run()
