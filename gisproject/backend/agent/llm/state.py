from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from typing_extensions import TypedDict


class AgentState(TypedDict):

    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    last_tool: str | None

    tool_errors: list[str]

    rag_result: dict[str, Any] | None

    mcp_results: list[dict[str, Any]]

    final_answer: str | None