from typing import Any, Awaitable, Callable, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from agent.graph import build_graph
from client.config import GIS_STDIO_SERVER
from client.manager import MCPClientManager

SYSTEM_PROMPT = (
    "You are a GIS assistant. Help the user with geospatial questions: "
    "maps, spatial analysis, coordinates, projections and GIS data. "
    "Use the available GIS tools when they help. Be concise and accurate. "
    "When the user attaches a file you are given its dataset_id; pass that "
    "dataset_id as the file path argument of any tool that needs the file."
)

_checkpointer = InMemorySaver()

ApprovalCallback = Callable[[dict], Awaitable[bool]]
TokenCallback = Callable[[str], Awaitable[None]]


class UserAgent:

    def __init__(self, session_id: str):
        self.session_id = session_id
        self._mcp = MCPClientManager([GIS_STDIO_SERVER])
        self._graph = None
        self._config = {"configurable": {"thread_id": session_id}}

    async def __aenter__(self):
        await self._mcp.__aenter__()
        try:
            self._graph = await build_graph(self._mcp, checkpointer=_checkpointer)
        except BaseException:
            await self._mcp.__aexit__(None, None, None)
            raise
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._mcp.__aexit__(exc_type, exc, tb)

    async def _start_messages(self) -> list:
        state = await self._graph.aget_state(self._config)
        if state.values.get("messages"):
            return []
        return [SystemMessage(content=SYSTEM_PROMPT)]

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
                f'dataset_id: {dataset["dataset_id"]}]\n{question}'
            )
        messages.append(HumanMessage(content=question))
        graph_input = {"messages": messages, "last_tool": None, "tool_errors": []}

        while graph_input is not None:
            interrupt_payload = None

            async for mode, data in self._graph.astream(
                graph_input,
                config=self._config,
                stream_mode=["messages", "updates"],
            ):
                if mode == "messages":
                    chunk, meta = data
                    if meta.get("langgraph_node") == "llm" and chunk.usage_metadata:
                        used += chunk.usage_metadata.get("total_tokens", 0)
                    if meta.get("langgraph_node") == "llm" and chunk.content:
                        await on_token(str(chunk.content))
                elif "__interrupt__" in data:
                    interrupt_payload = data["__interrupt__"][0].value

            if interrupt_payload is None:
                graph_input = None
            else:
                approved = await approve_tools(interrupt_payload)
                graph_input = Command(resume="approve" if approved else "reject")

        return used
