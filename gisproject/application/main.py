import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent),
)

import json
import anyio

from client.connect.base import MCPClient
from client.config import GIS_STDIO_SERVER

from agent.state import AgentState
from agent.llm import LLMClient
from agent.loop import AgentLoop
from agent.planner import Planner
from agent.mcp_adapter import mcp_tools_to_llm_tools


async def main() -> None:

    llm = LLMClient()

    async with MCPClient(
        GIS_STDIO_SERVER.transport
    ) as gis:

        # --------------------------------------------------
        # Get MCP tools
        # --------------------------------------------------

        mcp_tools = await gis.list_tools()

        llm_tools = mcp_tools_to_llm_tools(
            mcp_tools
        )

        # Optional: inspect one tool schema
        for tool in llm_tools:
            if tool["function"]["name"] == "calculate_area_tool":
                print(
                    json.dumps(tool, indent=2)
                )

        # --------------------------------------------------
        # Create Planner
        # --------------------------------------------------

        planner = Planner(
            llm=llm,
            tools=llm_tools,
        )

        # --------------------------------------------------
        # Create Agent
        # --------------------------------------------------

        agent = AgentLoop(
            llm=llm,
            mcp_client=gis,
            tools=llm_tools,
            planner=planner,
            max_iterations=50,
        )

        # --------------------------------------------------
        # System Prompt
        # --------------------------------------------------

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a GIS analysis agent.\n\n"

                    "Your job is to complete the user's entire "
                    "request using the available GIS tools.\n\n"

                    "Rules:\n"

                    "1. You must complete the ENTIRE user request.\n"

                    "2. Use GIS tools whenever the requested "
                    "operation can be performed by an available tool.\n"

                    "3. Do not calculate GIS results yourself when "
                    "a tool exists.\n"

                    "4. After receiving a tool result, determine "
                    "the NEXT required operation.\n"

                    "5. If the user's request requires another tool, "
                    "you MUST call that tool instead of writing "
                    "an explanation.\n"

                    "6. Do not change the user's task into a "
                    "different GIS problem.\n"

                    "7. Do not answer questions about Haversine "
                    "distance unless the user explicitly asks "
                    "for distance calculation.\n"

                    "8. Only return a final answer when the original "
                    "request is completely satisfied.\n"

                    "9. If a tool returns an error, analyze the "
                    "error before continuing.\n"

                    "10. Never claim that a tool succeeded when "
                    "it returned an error.\n"

                    "11. If the error can be corrected using the "
                    "available tools, try to correct it.\n"

                    "12. Do not repeatedly call the exact same "
                    "failed tool with the exact same arguments.\n"

                    "13. If the error cannot be recovered, clearly "
                    "explain the failure to the user.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    "Calculate the area of this polygon after "
                    "applying a 500 meter buffer.\n\n"

                    "Polygon:\n"
                    "POLYGON ((82 25, 82.01 25, "
                    "82.01 25.01, 82 25))\n\n"

                    "CRS: EPSG:4326."
                ),
            },
        ]

        # --------------------------------------------------
        # Create Agent State
        # --------------------------------------------------

        state = AgentState(
            messages=messages
        )

        # --------------------------------------------------
        # Run Agent
        # --------------------------------------------------

        try:
            answer = await agent.run(
                state
            )

        except Exception as exc:

            print(
                "\n========== AGENT ERROR =========="
            )

            print(
                type(exc).__name__
            )

            print(
                exc
            )

            answer = None

        # --------------------------------------------------
        # Generated Plan
        # --------------------------------------------------

        print(
            "\n========== GENERATED PLAN =========="
        )

        for step in state.plan:
            print(
                f"{step.step}. "
                f"{step.tool} - "
                f"{step.description}"
            )

        # --------------------------------------------------
        # Agent State
        # --------------------------------------------------

        print(
            "\n========== AGENT STATE =========="
        )

        print(
            "\nStatus:"
        )
        print(
            state.status
        )

        print(
            "\nIterations:"
        )
        print(
            state.iteration
        )

        print(
            "\nCurrent step:"
        )
        print(
            state.current_step
        )

        print(
            "\nTotal planned steps:"
        )
        print(
            len(state.plan)
        )

        print(
            "\nTool calls:"
        )
        print(
            json.dumps(
                state.tool_calls,
                indent=2
            )
        )

        print(
            "\nTool results:"
        )
        print(
            json.dumps(
                state.tool_results,
                indent=2
            )
        )

        print(
            "\nErrors:"
        )
        print(
            json.dumps(
                state.errors,
                indent=2
            )
        )

        # --------------------------------------------------
        # Final Answer
        # --------------------------------------------------

        print(
            "\n========== FINAL ANSWER =========="
        )

        print(
            answer
        )


if __name__ == "__main__":
    anyio.run(main)