from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

class AgentState(TypedDict):

    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    query: str

    thread_id: str

    last_tool: str | None

    last_tool_source: str | None

    tool_errors: list[str]

    rag_result: dict[str, Any] | None

    mcp_results: list[dict[str, Any]]
    web_rag_attempts: int
    retrieval_results: list[dict[str, Any]]

    evidence: list[dict[str, Any]]

    research_iteration: int

    max_research_iterations: int

    evidence_sufficient: bool | None

    evaluation_reason: str | None

    next_action: str | None

    evidence_quality: str | None

    citation_valid: bool | None

    citation_errors: list[str]

    final_answer: str | None