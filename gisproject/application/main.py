import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anyio
from client.connect.base import MCPClient
from client.config import GIS_STDIO_SERVER
from agent.llm import LLMClient
from agent.mcp_adapter import mcp_tools_to_ollama_tools
from agent.tool_executor import execute_mcp_tool

async def main() -> None:

    llm = LLMClient()

    async with MCPClient(
        GIS_STDIO_SERVER.transport
    ) as gis:

        # 1. Discover MCP tools
        mcp_tools = await gis.list_tools()

        # 2. Convert MCP -> Ollama format
        ollama_tools = mcp_tools_to_ollama_tools(
            mcp_tools
        )

        # 3. Initial conversation
        messages = [
            {
                "role": "user",
                "content": (
                    "Calculate the area of this polygon: "
                    "POLYGON ((82 25, "
                    "82.01 25, "
                    "82.01 25.01, "
                    "82 25)) "
                    "The CRS is EPSG:4326."
                ),
            }
        ]

        # 4. Ask Qwen
        tool_calls = []

        async for chunk in llm.chat(
            messages,
            tools=ollama_tools,
        ):
            if chunk.message.tool_calls:
                tool_calls.extend(
                    chunk.message.tool_calls
                )

        # Nothing to execute
        if not tool_calls:
            print("Qwen did not request a tool.")
            return

        # 5. Add assistant's tool-call message
        messages.append(
            {
                "role": "assistant",
                "tool_calls": tool_calls,
            }
        )

        # 6. Execute every requested tool
        for tool_call in tool_calls:

            tool_name = (
                tool_call.function.name
            )

            arguments = (
                tool_call.function.arguments
            )

            print("LLM selected:")
            print(tool_name)

            print("Arguments:")
            print(arguments)

            result = await execute_mcp_tool(
                gis,
                tool_name,
                arguments,
            )

            print("\nMCP RESULT:")
            print(result)

            # 7. Add tool result to conversation
            messages.append(
                {
                    "role": "tool",
                    "content": str(result),
                }
            )

        # 8. Ask Qwen again
        print("\nFINAL ANSWER:")

        async for chunk in llm.chat(
            messages,
            tools=ollama_tools,
        ):
            if chunk.message.content:
                print(
                    chunk.message.content,
                    end="",
                    flush=True,
                )

        print()


if __name__ == "__main__":
    anyio.run(main)