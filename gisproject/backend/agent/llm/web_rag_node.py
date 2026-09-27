from langchain_core.messages import ToolMessage

from agent.rag.main import WebRAG


def make_web_rag_node(web_rag: WebRAG):

    rag_graph = web_rag.get_graph()

    async def web_rag_node(state):

        message = state["messages"][-1]

        tool_call = next(
            call
            for call in message.tool_calls
            if call["name"] == "web_rag"
        )

        query = tool_call["args"]["query"]
        tool_call_id = tool_call["id"]

        result = await rag_graph.ainvoke(
            web_rag._initial_state(query),
            config={
                "configurable": {
                    "thread_id": state["thread_id"],
                }
            },
        )

        rag_result = {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "status": result.get("status", ""),
            "metrics": result.get("metrics", {}),
            "errors": result.get("errors", []),
        }

        return {
            "messages": [
                ToolMessage(
                    content=str(rag_result),
                    tool_call_id=tool_call_id,
                    name="web_rag",
                )
            ],
            "rag_result": rag_result,
            "evidence": [
                *state.get("evidence", []),
                {
                    "source": "web",
                    "tool": "web_rag",
                    "tool_call_id": tool_call_id,
                    "content": rag_result,
                },
            ],
            "research_iteration": (
                state.get("research_iteration", 0)
                + 1
            ),
            "web_rag_attempts": (
                state.get("web_rag_attempts", 0)
                + 1
            ),
        }

    return web_rag_node