from typing import Any
import json
import re
import uuid
from agent.planner import Planner
from agent.llm import LLMClient
from agent.tool_executor import execute_mcp_tool
from client.connect.base import MCPClient
from agent.state import AgentState

_TOOL_CALL_TAG_PATTERN = re.compile(
    r"<tool_call>\s*(\{.*?\})\s*</tool_call>",
    re.DOTALL,
)


def _extract_fallback_tool_call(
    content: str | None,
) -> dict[str, Any] | None:
    """Recover a tool call the model wrote as plain text instead of a
    structured tool_calls entry (e.g. <tool_call>{...}</tool_call>)."""

    if not content:
        return None

    match = _TOOL_CALL_TAG_PATTERN.search(content)

    if not match:
        return None

    try:
        data = json.loads(match.group(1))

    except json.JSONDecodeError:
        return None

    name = data.get("name")
    arguments = data.get("arguments")

    if not name or arguments is None:
        return None

    return {
        "id": f"fallback_{uuid.uuid4().hex[:16]}",
        "type": "function",
        "function": {
            "name": name,
            "arguments": json.dumps(arguments),
        },
    }


class AgentLoop:

    def __init__(
        self,
        llm: LLMClient,
        mcp_client: MCPClient,
        tools: list[dict[str, Any]],
        planner: Planner,
        max_iterations: int = 10,
        max_step_failures: int = 2,
        max_replans: int = 3,
    ):
        self.llm = llm
        self.mcp_client = mcp_client
        self.tools = tools
        self.planner = planner
        self.max_iterations = max_iterations
        self.max_step_failures = max_step_failures
        self.max_replans = max_replans

    def _get_active_tools(
        self,
        state: AgentState,
    ) -> list[dict[str, Any]]:

        if (
            not state.plan
            or state.current_step >= len(state.plan)
        ):
            return self.tools

        planned_tool_name = state.plan[state.current_step].tool

        active_tools = [
            tool
            for tool in self.tools
            if tool["function"]["name"] == planned_tool_name
        ]

        return active_tools or self.tools

    def _build_execution_messages(
        self,
        state: AgentState,
    ) -> list[dict[str, Any]]:

        if not state.plan:
            return state.messages

        current_step = state.current_step

        if current_step >= len(state.plan):
            completion_context = {
                "role": "system",
                "content": (
                    "The plan has been fully executed. Every "
                    "planned step has already been completed.\n\n"
                    "Do not call any more tools unless the user's "
                    "request genuinely requires one that the plan "
                    "missed.\n"
                    "Provide the final answer to the user's "
                    "original request now, using the results "
                    "already gathered."
                ),
            }

            return [
                completion_context,
                *state.messages,
            ]

        plan_text = "\n".join(
            f"{step.step}. {step.tool} - {step.description}"
            for step in state.plan
        )

        current_plan_step = state.plan[current_step]

        execution_context = {
            "role": "system",
            "content": (
                "You are executing a GIS task according to a plan.\n\n"

                "FULL PLAN:\n"
                f"{plan_text}\n\n"

                "CURRENT STEP:\n"
                f"{current_plan_step.step}. "
                f"{current_plan_step.tool} - "
                f"{current_plan_step.description}\n\n"

                "Execution rules:\n"
                "1. Execute the current step.\n"
                "2. Do not skip required steps.\n"
                "3. Use the planned tool for the current step.\n"
                "4. Use results from previous steps when required.\n"
                "5. Do not provide a final answer until the entire "
                "user request has been completed."
            ),
        }

        return [
            execution_context,
            *state.messages,
        ]

    async def run(
        self,
        state: AgentState,
    ) -> str:

        plan = await self.planner.create_plan(
            state.messages
        )

        state.plan = plan.steps

        for iteration in range(self.max_iterations):

            state.iteration = iteration + 1

            execution_messages = self._build_execution_messages(
                state
            )

            active_tools = self._get_active_tools(state)

            response = await self.llm.chat_once(
                execution_messages,
                tools=active_tools,
            )
            assistant_message = response.message

            if assistant_message.tool_calls:
                tool_call_dicts = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_message.tool_calls
                ]

            else:
                fallback_call = _extract_fallback_tool_call(
                    assistant_message.content
                )

                if fallback_call is None:

                    if response.finish_reason == "length":
                        state.status = "max_tokens"

                        raise RuntimeError(
                            "LLM stopped because it reached "
                            "the generation limit."
                        )

                    state.status = "completed"

                    return assistant_message.content or ""

                tool_call_dicts = [fallback_call]

            assistant_entry: dict[str, Any] = {
                "role": "assistant",
                "tool_calls": tool_call_dicts,
            }

            state.messages.append(assistant_entry)

            tool_call_dict = tool_call_dicts[0]

            tool_call_id = tool_call_dict["id"]
            tool_name = tool_call_dict["function"]["name"]

            arguments = json.loads(
                tool_call_dict["function"]["arguments"]
            )

            state.tool_calls.append(
                {
                    "tool_name": tool_name,
                    "arguments": arguments,
                }
            )

            planned_step = (
                state.plan[state.current_step]
                if state.plan
                and state.current_step < len(state.plan)
                else None
            )

            tool_failed = False

            try:

                result = await execute_mcp_tool(
                    self.mcp_client,
                    tool_name,
                    arguments,
                )

                state.tool_results.append(
                    {
                        "tool_name": tool_name,
                        "success": True,
                        "result": result,
                    }
                )

                if planned_step and tool_name == planned_step.tool:
                    state.current_step += 1
                    state.current_step_failures = 0

                tool_content = json.dumps(
                    {
                        "success": True,
                        "result": result,
                    }
                )

            except Exception as exc:

                tool_failed = True

                state.errors.append(
                    {
                        "tool_name": tool_name,
                        "error": str(exc),
                    }
                )

                tool_content = json.dumps(
                    {
                        "success": False,
                        "tool": tool_name,
                        "error": str(exc),
                    }
                )

            tool_message = {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": tool_content,
            }

            state.messages.append(tool_message)

            if tool_failed and planned_step is not None:
                state.current_step_failures += 1

                if state.current_step_failures >= self.max_step_failures:
                    await self._replan(state)

        state.status = "max_iterations"

        raise RuntimeError(
            "Agent exceeded maximum iterations: "
            f"{self.max_iterations}"
        )

    async def _replan(
        self,
        state: AgentState,
    ) -> None:

        state.replans += 1

        if state.replans > self.max_replans:
            state.status = "replan_failed"

            raise RuntimeError(
                "Agent exceeded maximum re-planning attempts "
                f"({self.max_replans})."
            )

        new_plan = await self.planner.replan(
            messages=state.messages,
            current_plan=state.plan,
            current_step=state.current_step,
        )

        state.plan = new_plan.steps
        state.current_step = 0
        state.current_step_failures = 0
