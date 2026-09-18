# import sys
# from pathlib import Path

# sys.path.insert(
#     0,
#     str(Path(__file__).resolve().parent.parent),
# )
# from agent.tools import create_mcp_tool

# from client.manager import MCPClientManager, MCPClient
# from client.config import GIS_STDIO_SERVER as GIS_SERVER
# from agent.main import create_agent

# async def main():

#     async with MCPClientManager([GIS_SERVER]) as manager:
#         mcp_tools = await manager.list_tools()

#         langchain_tools = [
#             create_mcp_tool(manager, tool)
#             for tool in mcp_tools
#         ]
#         agent = create_agent(
#             model=model,
#             tools=langchain_tools,
#         )
