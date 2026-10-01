from typing import Any, Awaitable, Callable, Dict

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
from langgraph.types import Command

from app.api.service.agent.runtime import AgentRuntime


SYSTEM_PROMPT = """
You are a GIS research assistant.

You have access to five types of capabilities:

1. Runtime tools
   Use runtime tools for application/runtime information.
   For current date or time questions, use
   get_current_datetime.

2. GIS MCP tools
   Use GIS MCP tools for spatial operations,
   geometry calculations, CRS operations,
   and GIS computation.

3. Google Earth Engine (GEE) MCP tools
   Use GEE tools to search satellite imagery
   (for example Sentinel-2) for a bounding box
   and date range.
   - search_satellite_images needs a bbox in WGS84
     (min_lon, min_lat, max_lon, max_lat) and
     start_date / end_date in YYYY-MM-DD format.
   - If the user gives a place name instead of a
     bbox, or leaves out dates, ask for the missing
     details. Do not invent coordinates or dates.
   - For relative dates such as "last month", call
     get_current_datetime first.
   - Report only what the tool returns. Never make
     up image IDs, dates, or cloud percentages.

4. Internal GIS knowledge
   Use the internal knowledge base for stable GIS
   concepts, documentation, projections, CRS,
   remote sensing, and spatial analysis concepts.

5. Web research
   Use web research for current, recent,
   latest, or internet-based information.

IMPORTANT TEMPORAL RULES:

- Never assume the current date or time from your
  pretrained knowledge.
- When the question depends on the current date or time,
  use get_current_datetime.
- Treat the result of get_current_datetime as authoritative.
- Never compare a runtime datetime with your pretrained
  knowledge.
- Never claim that a runtime timestamp is in the future
  or past based on your internal knowledge.

Examples:

"What is the current time?"
→ get_current_datetime

"What is today's date?"
→ get_current_datetime

"What is the latest NISAR news?"
→ get_current_datetime first,
  then web research

"What is EPSG:4326?"
→ internal GIS knowledge

"Calculate the area of this polygon."
→ GIS MCP tool

"Find Sentinel-2 images over this bbox for
 January 2025 with less than 10% cloud."
→ GEE MCP tool (search_satellite_images)

"Find satellite images of Varanasi from last month."
→ get_current_datetime, then ask for a bbox
  (or confirm one) before calling the GEE tool
"""


ApprovalCallback = Callable[
    [dict],
    Awaitable[bool],
]

TokenCallback = Callable[
    [str],
    Awaitable[None],
]


class UserAgent:

    def __init__(
        self,
        runtime: AgentRuntime,
        session_id: str,
    ):
        self.runtime = runtime
        self.session_id = session_id

        self._graph = runtime.graph

        self._config = {
            "configurable": {
                "thread_id": session_id,
            }
        }

    async def _start_messages(self):

        state = await self._graph.aget_state(
            self._config
        )

        if state.values.get("messages"):
            return []

        return [
            SystemMessage(
                content=SYSTEM_PROMPT
            )
        ]

    async def ask(
        self,
        question: str,
        on_token: TokenCallback,
        approve_tools: ApprovalCallback,
        dataset: Dict[str, Any] | None = None,
    ) -> int:

        used = 0

        messages = await self._start_messages()

        if dataset:

            question = (
                f'[Attached file "{dataset["filename"]}" '
                f'(format: {dataset["format"]}), '
                f'dataset_id: {dataset["dataset_id"]}]\n'
                f"{question}"
            )

        messages.append(
            HumanMessage(
                content=question
            )
        )

        graph_input = {
            "messages": messages,
            "query": question,
            "thread_id": self.session_id,

            "last_tool": None,
            "last_tool_source": None,
            "tool_errors": [],

            "rag_result": None,
            "mcp_results": [],
            "retrieval_results": [],

            "evidence": [],

            "research_iteration": 0,
            "max_research_iterations": 8,

            "web_rag_attempts": 0,

            "evidence_sufficient": None,
            "evaluation_reason": None,
            "next_action": None,

            "evidence_quality": None,
            "citation_valid": None,
            "citation_errors": [],

            "final_answer": None,
        }

        while graph_input is not None:

            interrupt_payload = None

            async for mode, data in self._graph.astream(
                graph_input,
                config=self._config,
                stream_mode=[
                    "messages",
                    "updates",
                    "custom",
                ],
            ):

                # ==========================================
                # MESSAGE STREAM
                # ==========================================

                if mode == "messages":

                    chunk, meta = data

                    node_name = meta.get(
                        "langgraph_node"
                    )

                    usage_metadata = getattr(
                        chunk,
                        "usage_metadata",
                        None,
                    )

                

                    if (
                        node_name == "llm"
                        and usage_metadata
                    ):

                        used += usage_metadata.get(
                            "total_tokens",
                            0,
                        )


                elif mode == "custom":

                    if (
                        isinstance(data, dict)
                        and data.get("type")
                        == "answer_token"
                    ):

                        await on_token(
                            str(
                                data["content"]
                            )
                        )
                elif mode == "updates":



                    if "__interrupt__" in data:

                        interrupt_payload = (
                            data[
                                "__interrupt__"
                            ][0].value
                        )

    

            if interrupt_payload is None:

                graph_input = None

            else:

                approved = await approve_tools(
                    interrupt_payload
                )

                graph_input = Command(
                    resume=(
                        "approve"
                        if approved
                        else "reject"
                    )
                )

        return used
