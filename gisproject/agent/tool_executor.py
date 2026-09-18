from typing import Any
from client.manager import MCPClient
async def execute_mcp_tool(
    client: MCPClient,
    tool_name: str,
    arguments: dict[str, Any],
):
    if (
            "payload" in arguments
            and isinstance(arguments["payload"], dict)
        ):
            mcp_arguments = arguments

    else:
        mcp_arguments = {
            "payload": arguments
        }

    return await client.execute_tool(
        tool_name,
        mcp_arguments,
    )