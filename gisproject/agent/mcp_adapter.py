from mcp.types import ListToolsResult


def mcp_tools_to_ollama_tools(
    mcp_tools: ListToolsResult,
) -> list[dict]:
    """Convert MCP tool definitions to Ollama tool definitions."""

    ollama_tools = []

    for tool in mcp_tools.tools:
        ollama_tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                },
            }
        )

    return ollama_tools