from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
    AIMessage
)

from langgraph.config import get_stream_writer

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

    evaluate = make_evidence_quality_evaluator(llm)

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


        if result is None:

            return {
                "evidence_quality": "weak",
                "citation_valid": False,
                "citation_errors": [
                    "Evidence quality evaluator "
                    "returned no result."
                ],
            }

        return {
            "evidence_quality": result.quality,
            "citation_valid": result.citation_valid,
            "citation_errors": result.errors,
        }

    return evidence_quality_node



def make_final_answer_node(llm):

    async def final_answer(state):

        query = state["query"]

        evidence = state.get(
            "evidence",
            [],
        )

        evaluation_reason = state.get(
            "evaluation_reason"
        )

        evidence_quality = state.get(
            "evidence_quality"
        )

        citation_errors = state.get(
            "citation_errors",
            [],
        )

        prompt = f"""
You are the final answer generator for a GIS research assistant.

User question:
{query}

Evidence collected by the research system:
{evidence}

Evidence evaluation:
{evaluation_reason}

Evidence quality:
{evidence_quality}

Citation errors:
{citation_errors}

Rules:

1. Answer the user's question directly.

2. Use the collected evidence as the authoritative
   source for factual claims.

3. For runtime/tool results such as current date,
   current time, system state, or application state,
   treat the tool result as authoritative.

4. Never replace a runtime/tool result with your
   pretrained knowledge.

5. If the user asks for the current date or time,
   use the result from get_current_datetime.

6. For web research, use the retrieved sources
   to support factual claims.

7. Do not invent facts that are not supported
   by the evidence.

8. Do not mention internal agent steps.

9. Do not mention evidence evaluation.

10. Do not mention internal tools unless the user
    explicitly asks how the answer was obtained.

11. If sources are available, cite the relevant
    sources in the final answer.

12. If the evidence does not support a claim,
    say that the available evidence does not
    establish it.
"""

        messages = [
            *state["messages"],
            SystemMessage(
                content=prompt
            ),
        ]

        writer = get_stream_writer()

        response_content = ""

        async for chunk in llm.astream(
            messages
        ):

            if not chunk.content:
                continue

            content = str(
                chunk.content
            )

            response_content += content

            writer(
                {
                    "type": "answer_token",
                    "content": content,
                }
            )

        return {
            "messages": [
                AIMessage(
                    content=response_content
                )
            ],
            "final_answer": response_content,
        }

    return final_answer





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