from mcp.types import ListToolsResult


def mcp_tools_to_llm_tools(
    mcp_tools: ListToolsResult,
) -> list[dict]:
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