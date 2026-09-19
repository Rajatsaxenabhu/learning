from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt
from agent.llm.model import model
from agent.service.tools import discover_tools
from agent.state import AgentState


MCP_SERVER_NAME = "gis_local"


def make_llm_node(llm):
    async def llm_node(state: AgentState):
        response = await llm.ainvoke(
            state["messages"]
        )

        return {
            "messages": [response]
        }

    return llm_node

def make_tools_node(tools):

    tool_node = ToolNode(
        tools,
        handle_tool_errors=True,
    )

    async def tools_node(state: AgentState):

        approval = interrupt({
            "type": "tool_approval",
            "message": "Approve GIS tool execution?",
            "tools": [
                call["name"]
                for call in state["messages"][-1].tool_calls
            ],
        })

        if approval != "approve":
            return {
                "messages": [
                    ToolMessage(
                        content="Tool execution rejected by user.",
                        tool_call_id=call["id"],
                        name=call["name"],
                    )
                    for call in state["messages"][-1].tool_calls
                ],
                "tool_errors": [
                    "Tool execution rejected by user."
                ],
            }

        result = await tool_node.ainvoke(state)

        last_tool = None
        tool_errors = list(
            state.get("tool_errors", [])
        )

        if state["messages"]:
            message = state["messages"][-1]

            if (
                hasattr(message, "tool_calls")
                and message.tool_calls
            ):
                last_tool = message.tool_calls[0]["name"]

        for message in result.get("messages", []):

            if getattr(message, "is_error", False):
                tool_errors.append(
                    str(message.content)
                )

        return {
            **result,
            "last_tool": last_tool,
            "tool_errors": tool_errors,
        }

    return tools_node

async def build_graph(mcp_manager, checkpointer=None):
    tools = await discover_tools(
        mcp_manager,
        MCP_SERVER_NAME,
    )

    builder = StateGraph(AgentState)

    llm = model.bind_tools(tools)

    builder.add_node(
        "llm",
        make_llm_node(llm),
    )

    builder.add_node(
        "tools",
        make_tools_node(tools),
    )

    builder.add_edge(
        START,
        "llm",
    )

    builder.add_conditional_edges(
        "llm",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )

    builder.add_edge(
        "tools",
        "llm",
    )

    return builder.compile(
        checkpointer=checkpointer
    )