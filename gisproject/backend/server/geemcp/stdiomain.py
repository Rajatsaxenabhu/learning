from server.geemcp.config.logging import logger
from server.geemcp.server import mcp
from server.geemcp.config.gee import initialize_gee
from server.geemcp import tools

def main():

    initialize_gee()
    logger.info("initialize GEE ")
    logger.info("Starting GEE MCP server over stdio")
    mcp.run()
if __name__ == "__main__":
    main()
