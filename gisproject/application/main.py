import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)
import json
import anyio

from client.connect.base import MCPClient
from client.config import GIS_STDIO_SERVER

from agent.llm import LLMClient
from agent.loop import AgentLoop
from agent.mcp_adapter import mcp_tools_to_ollama_tools


async def main() -> None:

    llm = LLMClient()

    async with MCPClient(
        GIS_STDIO_SERVER.transport
    ) as gis:

        mcp_tools = await gis.list_tools()
        ollama_tools = mcp_tools_to_ollama_tools(
            mcp_tools
        )
        for tool in ollama_tools:
            if tool["function"]["name"] == "buffer_geometry_tool":
                print(
                    json.dumps(tool, indent=2)
                )
        agent = AgentLoop(
            llm=llm,
            mcp_client=gis,
            tools=ollama_tools,
        )

        # 4. User request
        messages = [
                {
            "role": "system",
            "content": (
                "You are a GIS analysis agent.\n\n"

                "Your job is to complete the user's entire request "
                "using the available GIS tools.\n\n"

                "Rules:\n"
                "1. You must complete the ENTIRE user request.\n"
                "2. Use GIS tools whenever the requested operation can be "
                "performed by an available tool.\n"
                "3. Do not calculate GIS results yourself when a tool exists.\n"
                "4. After receiving a tool result, determine the NEXT required "
                "operation.\n"
                "5. If the user's request requires another tool, you MUST call "
                "that tool instead of writing an explanation.\n"
                "6. Do not change the user's task into a different GIS problem.\n"
                "7. Do not answer questions about Haversine distance unless "
                "the user explicitly asks for distance calculation.\n"
                "8. Only return a final answer when the original request is "
                "completely satisfied.\n"
            ),
        }
        ]

        # 5. Run agent
        answer = await agent.run(messages)

        print("\nFINAL ANSWER:")
        print(answer)


if __name__ == "__main__":
    anyio.run(main)