from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import StructuredTool

from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt

from agent.llm.model import model
from agent.llm.state import AgentState
from agent.llm.web_rag_node import make_web_rag_node
from agent.llm.evidence_evaluator import (
    make_evidence_evaluator,
)
from agent.llm.evidence_quality import (
    make_evidence_quality_evaluator,
)
from agent.service.knowledge import (
    create_knowledge_tool,
)
from agent.service.tools import discover_tools
from agent.service.runtime import (
    get_current_datetime,
)


MCP_SERVER_NAME = "gis_local"

WEB_RAG_TOOL_NAME = "web_rag"

MAX_RESEARCH_ITERATIONS = 8


def create_web_rag_tool():

    async def web_rag(query: str) -> str:
        return query

    tool = StructuredTool.from_function(
        coroutine=web_rag,
        name=WEB_RAG_TOOL_NAME,
        description=(
            "Research information from external web sources.\n\n"
            "Use this when:\n"
            "- the user asks for current or latest information\n"
            "- the information may have changed recently\n"
            "- external sources are required\n"
            "- the internal knowledge base does not contain enough information\n"
            "- the user explicitly asks to search the web\n\n"
            "Do not use this for:\n"
            "- inspecting an uploaded GIS dataset\n"
            "- performing GIS calculations\n"
            "- stable GIS concepts that can be answered from "
            "the internal knowledge base"
        ),
    )

    tool.metadata = {
        "read_only": True,
        "source": "web",
    }

    return tool


def make_llm_node(llm):

    async def llm_node(
        state: AgentState,
    ):

        response = await llm.ainvoke(
            state["messages"]
        )

        return {
            "messages": [response]
        }

    return llm_node


def make_tools_node(tools):

    read_only = {
        tool.name: bool(
            (tool.metadata or {}).get(
                "read_only"
            )
        )
        for tool in tools
    }

    tool_metadata = {
        tool.name: tool.metadata or {}
        for tool in tools
    }

    tool_node = ToolNode(
        tools,
        handle_tool_errors=True,
    )

    async def tools_node(
        state: AgentState,
    ):

        tool_calls = (
            state["messages"][-1].tool_calls
        )

        needs_approval = [
            call["name"]
            for call in tool_calls
            if not read_only.get(
                call["name"],
                False,
            )
        ]

        approval = "approve"

        if needs_approval:

            approval = interrupt(
                {
                    "type": "tool_approval",
                    "message": (
                        "Approve tool execution?"
                    ),
                    "tools": needs_approval,
                }
            )

        if approval != "approve":

            return {
                "messages": [
                    ToolMessage(
                        content=(
                            "Tool execution rejected "
                            "by user."
                        ),
                        tool_call_id=call["id"],
                        name=call["name"],
                    )
                    for call in tool_calls
                ],
                "tool_errors": [
                    "Tool execution rejected by user."
                ],
            }

        result = await tool_node.ainvoke(
            state
        )

        mcp_results = list(
            state.get(
                "mcp_results",
                [],
            )
        )

        evidence = list(
            state.get(
                "evidence",
                [],
            )
        )

        last_tool = None
        last_tool_source = None

        if tool_calls:

            last_tool = tool_calls[-1]["name"]

            last_tool_source = (
                tool_metadata.get(
                    last_tool,
                    {},
                ).get(
                    "source",
                    "unknown",
                )
            )

        for message in result.get(
            "messages",
            [],
        ):

            content = getattr(
                message,
                "content",
                None,
            )

            if not content:
                continue

            name = getattr(
                message,
                "name",
                None,
            )

            tool_call_id = getattr(
                message,
                "tool_call_id",
                None,
            )

            metadata = tool_metadata.get(
                name,
                {},
            )

            source = metadata.get(
                "source",
                "unknown",
            )

            mcp_results.append(
                {
                    "content": content,
                    "tool_call_id": tool_call_id,
                    "name": name,
                    "source": source,
                }
            )

            evidence.append(
                {
                    "id": (
                        f"evidence_"
                        f"{len(evidence) + 1}"
                    ),
                    "source": source,
                    "tool": name,
                    "tool_call_id": tool_call_id,
                    "content": content,
                }
            )

        return {
            **result,
            "last_tool": last_tool,
            "last_tool_source": last_tool_source,
            "mcp_results": mcp_results,
            "evidence": evidence,
            "research_iteration": (
                state.get(
                    "research_iteration",
                    0,
                )
                + 1
            ),
        }

    return tools_node


def make_evidence_evaluation_node(llm):

    evaluate = make_evidence_evaluator(
        llm
    )

    async def evidence_evaluation_node(
        state: AgentState,
    ):

        result = await evaluate(
            query=state["query"],
            evidence=state.get(
                "evidence",
                [],
            ),
        )

        return {
            "evidence_sufficient": (
                result.sufficient
            ),
            "evaluation_reason": (
                result.reason
            ),
            "next_action": (
                result.next_action
            ),
        }

    return evidence_evaluation_node


def make_evidence_quality_node(llm):

    evaluate = (
        make_evidence_quality_evaluator(
            llm
        )
    )

    async def evidence_quality_node(
        state: AgentState,
    ):

        result = await evaluate(
            query=state["query"],
            evidence=state.get(
                "evidence",
                [],
            ),
        )

        return {
            "evidence_quality": result.quality,
            "citation_valid": (
                result.citation_valid
            ),
            "citation_errors": result.errors,
        }

    return evidence_quality_node


def make_final_answer_node(llm):

    async def final_answer_node(
        state: AgentState,
    ):

        response = await llm.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You are the final answer generator "
                        "for a GIS research assistant.\n\n"
                        "Answer the user's question using "
                        "the available evidence.\n\n"
                        "Rules:\n"
                        "- Use only information supported "
                        "by the evidence.\n"
                        "- Do not invent information.\n"
                        "- If evidence is incomplete, "
                        "state the limitation.\n"
                        "- Prefer concise and direct answers.\n"
                        "- When source information is available, "
                        "include appropriate source references."
                    )
                ),
                HumanMessage(
                    content=(
                        f"User question:\n"
                        f"{state['query']}\n\n"
                        f"Evidence:\n"
                        f"{state.get('evidence', [])}\n\n"
                        f"Evidence evaluation:\n"
                        f"{state.get('evaluation_reason', '')}\n\n"
                        f"Evidence quality:\n"
                        f"{state.get('evidence_quality', '')}\n\n"
                        f"Citation errors:\n"
                        f"{state.get('citation_errors', [])}"
                    )
                ),
            ]
        )

        return {
            "messages": [response],
            "final_answer": response.content,
        }

    return final_answer_node


def route_after_llm(
    state: AgentState,
):

    message = state["messages"][-1]

    tool_calls = getattr(
        message,
        "tool_calls",
        None,
    )

    if not tool_calls:
        return "answer"

    research_iteration = state.get(
        "research_iteration",
        0,
    )

    max_iterations = state.get(
        "max_research_iterations",
        MAX_RESEARCH_ITERATIONS,
    )

    if research_iteration >= max_iterations:
        return "answer"

    tool_names = {
        call["name"]
        for call in tool_calls
    }

    if WEB_RAG_TOOL_NAME in tool_names:
        return "web_rag"

    return "tools"


def route_after_tools(
    state: AgentState,
):

    source = state.get(
        "last_tool_source"
    )

    if source in {
        "runtime",
        "gis_mcp",
    }:
        return "llm"

    if source == "qdrant":
        return "evaluate_evidence"

    return "llm"


def route_after_evaluation(
    state: AgentState,
):

    if state.get(
        "evidence_sufficient",
        False,
    ):
        return "evaluate_quality"

    research_iteration = state.get(
        "research_iteration",
        0,
    )

    max_iterations = state.get(
        "max_research_iterations",
        MAX_RESEARCH_ITERATIONS,
    )

    if research_iteration >= max_iterations:
        return "evaluate_quality"

    next_action = state.get(
        "next_action"
    )

    web_rag_attempts = state.get(
        "web_rag_attempts",
        0,
    )

    if (
        next_action == "web_rag"
        and web_rag_attempts >= 1
    ):
        return "answer"

    return "llm"


def route_after_quality(
    state: AgentState,
):

    citation_valid = state.get(
        "citation_valid",
        False,
    )

    research_iteration = state.get(
        "research_iteration",
        0,
    )

    max_iterations = state.get(
        "max_research_iterations",
        MAX_RESEARCH_ITERATIONS,
    )

    if citation_valid:
        return "answer"

    if research_iteration >= max_iterations:
        return "answer"

    return "llm"


async def build_graph(
    mcp_manager,
    web_rag,
    knowledge_retriever,
    checkpointer=None,
):

    mcp_tools = await discover_tools(
        mcp_manager,
        MCP_SERVER_NAME,
    )

    knowledge_tool = create_knowledge_tool(
        knowledge_retriever
    )

    web_rag_tool = create_web_rag_tool()

    runtime_tools = [
        get_current_datetime,
    ]

    all_tools = [
        *mcp_tools,
        *runtime_tools,
        knowledge_tool,
        web_rag_tool,
    ]

    llm = model.bind_tools(
        all_tools
    )

    builder = StateGraph(
        AgentState
    )

    builder.add_node(
        "llm",
        make_llm_node(llm),
    )

    agent_tools = [
        *mcp_tools,
        *runtime_tools,
        knowledge_tool,
    ]

    builder.add_node(
        "tools",
        make_tools_node(
            agent_tools
        ),
    )

    builder.add_node(
        "web_rag",
        make_web_rag_node(
            web_rag
        ),
    )

    builder.add_node(
        "evaluate_evidence",
        make_evidence_evaluation_node(
            model
        ),
    )

    builder.add_node(
        "evaluate_quality",
        make_evidence_quality_node(
            model
        ),
    )

    builder.add_node(
        "answer",
        make_final_answer_node(
            model
        ),
    )

    builder.add_edge(
        START,
        "llm",
    )

    builder.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "tools": "tools",
            "web_rag": "web_rag",
            "answer": "answer",
        },
    )

    builder.add_conditional_edges(
        "tools",
        route_after_tools,
        {
            "llm": "llm",
            "evaluate_evidence": (
                "evaluate_evidence"
            ),
        },
    )

    builder.add_edge(
        "web_rag",
        "evaluate_evidence",
    )

    builder.add_conditional_edges(
        "evaluate_evidence",
        route_after_evaluation,
        {
            "evaluate_quality": (
                "evaluate_quality"
            ),
            "llm": "llm",
            "answer": "answer",
        },
    )

    builder.add_conditional_edges(
        "evaluate_quality",
        route_after_quality,
        {
            "answer": "answer",
            "llm": "llm",
        },
    )

    builder.add_edge(
        "answer",
        END,
    )

    return builder.compile(
        checkpointer=checkpointer
    )