from typing import Any
import json

from pydantic import BaseModel, ValidationError

from agent.llm import LLMClient


class PlanStep(BaseModel):
    step: int
    tool: str
    description: str


class Plan(BaseModel):
    steps: list[PlanStep]


class Planner:

    def __init__(
        self,
        llm: LLMClient,
        tools: list[dict[str, Any]],
    ):
        self.llm = llm
        self.tools = tools

    def _get_available_tool_names(self) -> list[str]:
        return [
            tool["function"]["name"]
            for tool in self.tools
        ]

    async def create_plan(
        self,
        messages: list[dict[str, Any]],
    ) -> Plan:

        available_tools = self._get_available_tool_names()

        planning_messages = [
            {
                "role": "system",
                "content": (
                    "You are a GIS task planner.\n\n"

                    "Your job is to break the user's request "
                    "into a small sequence of concrete GIS steps.\n\n"

                    "For each step provide:\n"
                    "- step: sequential step number\n"
                    "- tool: exact GIS tool name\n"
                    "- description: what the step accomplishes\n\n"

                    "Available GIS tools:\n"
                    f"{json.dumps(available_tools, indent=2)}\n\n"

                    "Rules:\n"
                    "1. Use only tools from the available tool list.\n"
                    "2. Do not invent tool names.\n"
                    "3. Do not provide tool arguments yet.\n"
                    "4. Respect dependencies between steps.\n"
                    "5. A later step may depend on the result of an earlier step.\n"
                    "6. Include only steps required to complete the user's request.\n\n"

                    "Return ONLY valid JSON in this format:\n"
                    "{\n"
                    '  "steps": [\n'
                    "    {\n"
                    '      "step": 1,\n'
                    '      "tool": "buffer_geometry_tool",\n'
                    '      "description": "Buffer the polygon by 500 meters"\n'
                    "    },\n"
                    "    {\n"
                    '      "step": 2,\n'
                    '      "tool": "calculate_area_tool",\n'
                    '      "description": "Calculate the area of the buffered polygon"\n'
                    "    }\n"
                    "  ]\n"
                    "}"
                ),
            },
            *messages,
        ]

        response = await self.llm.chat_once(
            planning_messages
        )

        content = response.message.content or ""

        try:
            data = json.loads(content)

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Planner returned invalid JSON."
            ) from exc

        try:
            plan = Plan.model_validate(data)

        except ValidationError as exc:
            raise RuntimeError(
                "Planner returned an invalid plan structure."
            ) from exc

        available_tool_set = set(available_tools)

        for step in plan.steps:
            if step.tool not in available_tool_set:
                raise RuntimeError(
                    f"Planner selected unavailable tool: "
                    f"{step.tool}"
                )

        return plan

    async def replan(
        self,
        messages: list[dict[str, Any]],
        current_plan: list[PlanStep],
        current_step: int,
    ) -> Plan:

        available_tools = [
            {
                "name": tool["function"]["name"],
                "description": tool["function"]["description"],
                "parameters": tool["function"]["parameters"],
            }
            for tool in self.tools
        ]

        current_plan_text = "\n".join(
            f"{step.step}. {step.tool} - {step.description}"
            for step in current_plan
        )

        planning_messages = [
            {
                "role": "system",
                "content": (
                    "You are a GIS task re-planner.\n\n"

                    "The original GIS task could not be completed "
                    "according to the current plan.\n\n"

                    "Analyze the conversation, tool results, and "
                    "errors and create a corrected plan.\n\n"

                    "Available GIS tools:\n"
                    f"{json.dumps(available_tools, indent=2)}\n\n"

                    "Current plan:\n"
                    f"{current_plan_text}\n\n"

                    f"Current step index: {current_step}\n\n"

                    "Rules:\n"
                    "1. Complete the original user request.\n"
                    "2. Use only available tools.\n"
                    "3. Do not invent tools.\n"
                    "4. Do not provide tool arguments yet.\n"
                    "5. Correct the problem indicated by the error.\n"
                    "6. Preserve successful previous work when possible.\n"
                    "7. Include only required steps.\n\n"

                    "Return ONLY valid JSON:\n"
                    "{\n"
                    '  "steps": [\n'
                    "    {\n"
                    '      "step": 1,\n'
                    '      "tool": "tool_name",\n'
                    '      "description": "what this step does"\n'
                    "    }\n"
                    "  ]\n"
                    "}"
                ),
            },
            *messages,
        ]

        response = await self.llm.chat_once(
            planning_messages
        )

        content = response.message.content or ""

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Re-planner returned invalid JSON."
            ) from exc

        try:
            plan = Plan.model_validate(data)
        except ValidationError as exc:
            raise RuntimeError(
                "Re-planner returned an invalid plan structure."
            ) from exc

        available_tool_set = {
            tool["function"]["name"]
            for tool in self.tools
        }

        for step in plan.steps:
            if step.tool not in available_tool_set:
                raise RuntimeError(
                    f"Re-planner selected unavailable tool: "
                    f"{step.tool}"
                )

        return plan