from typing import Any
from client.manager import MCPClient
async def execute_mcp_tool(
    client: MCPClient,
    tool_name: str,
    arguments: dict[str, Any],
):
    """
    Execute an MCP tool selected by the LLM.
    """

    if (
            "payload" in arguments
            and isinstance(arguments["payload"], dict)
        ):
            mcp_arguments = arguments

    else:
        mcp_arguments = {
            "payload": arguments
        }

    print("Arguments sent to MCP:")
    print(mcp_arguments)

    return await client.execute_tool(
        tool_name,
        mcp_arguments,
    )