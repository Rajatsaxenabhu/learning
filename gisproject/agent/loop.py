from typing import Any
import json
from agent.llm import LLMClient
from agent.tool_executor import execute_mcp_tool
from client.connect.base import MCPClient


class AgentLoop:

    def __init__(
        self,
        llm: LLMClient,
        mcp_client: MCPClient,
        tools: list[dict[str, Any]],
        max_iterations: int = 10,
    ):
        self.llm = llm
        self.mcp_client = mcp_client
        self.tools = tools
        self.max_iterations = max_iterations

    async def run(
        self,
        messages: list[dict[str, Any]],
    ) -> str:

        for iteration in range(self.max_iterations):

            print(f"\n--- Agent iteration {iteration + 1} ---")

            print("\nMESSAGES SENT TO LLM:")

            for i, message in enumerate(messages):
                print(f"\nMESSAGE {i}:")
                print(message)

            response = await self.llm.chat_once(
                messages,
                tools=self.tools,
            )

            print("\nRAW LLM RESPONSE:")
            print(response)

            assistant_message = response.message

            # LLM has finished
            if not assistant_message.tool_calls:
                print("\nLLM FINISHED")
                return assistant_message.content or ""

            messages.append(
                assistant_message.model_dump(
                    exclude_none=True
                )
            )

            tool_call = assistant_message.tool_calls[0]

            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments

            print("\nLLM SELECTED TOOL:")
            print(tool_name)

            print("\nTOOL ARGUMENTS:")
            print(arguments)

            try:
                result = await execute_mcp_tool(
                    self.mcp_client,
                    tool_name,
                    arguments,
                )

                print("\nMCP RESULT:")
                print(result)

                tool_content = json.dumps(result)

            except Exception as exc:

                print("\nMCP ERROR:")
                print(exc)

                tool_content = (
                    f"Tool execution failed.\n"
                    f"Tool: {tool_name}\n"
                    f"Error: {exc}"
                )

            tool_message = {
                "role": "tool",
                "tool_name": tool_name,
                "content": tool_content,
            }

            print("\nTOOL MESSAGE ADDED:")
            print(tool_message)

            messages.append(tool_message)

        raise RuntimeError(
            "Agent exceeded maximum iterations: "
            f"{self.max_iterations}"
        )