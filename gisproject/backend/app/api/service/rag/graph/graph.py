from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.api.service.rag.graph.state import RAGState
from app.api.service.rag.graph.nodes import RAGNodes

from app.api.service.rag.graph.routes import (
    after_freshness,
    after_search,
    after_extract,
    after_chunk,
    after_retrieve,
    after_rerank,
    after_evaluation,
    after_refine,
    after_generate,
    after_repair,
    after_memory_evaluation,
)


def build_rag_graph(
    search_service,
    extractor,
    chunker,
    vector_store,
    bm25_retriever,
    reranker,
    rewriter,
    evaluator,
    refiner,
    llm,
    checkpointer=None,
):

    nodes = RAGNodes(
        search_service=search_service,
        extractor=extractor,
        chunker=chunker,
        vector_store=vector_store,
        bm25_retriever=bm25_retriever,
        reranker=reranker,
        rewriter=rewriter,
        evaluator=evaluator,
        refiner=refiner,
        llm=llm,
    )

    builder = StateGraph(RAGState)

    builder.add_node(
        "start_request",
        nodes.start_request,
    )

    builder.add_node(
        "rewrite",
        nodes.rewrite,
    )

    builder.add_node(
        "detect_search_intent",
        nodes.detect_search_intent,
    )

    builder.add_node(
        "detect_freshness",
        nodes.detect_freshness,
    )

    builder.add_node(
        "retrieve_memory",
        nodes.retrieve_memory,
    )

    builder.add_node(
        "evaluate_memory",
        nodes.evaluate_memory,
    )

    builder.add_node(
        "search",
        nodes.search,
    )

    builder.add_node(
        "retry_search",
        nodes.retry_search,
    )

    builder.add_node(
        "extract",
        nodes.extract,
    )

    builder.add_node(
        "chunk",
        nodes.chunk,
    )

    builder.add_node(
        "retrieve",
        nodes.retrieve,
    )

    builder.add_node(
        "rerank",
        nodes.rerank,
    )

    builder.add_node(
        "evaluate",
        nodes.evaluate,
    )

    builder.add_node(
        "refine",
        nodes.refine,
    )

    builder.add_node(
        "generate",
        nodes.generate,
    )

    builder.add_node(
        "repair_citations",
        nodes.repair_citations,
    )

    builder.add_node(
        "finish_request",
        nodes.finish_request,
    )

    builder.add_node(
        "fail",
        nodes.fail,
    )

    builder.add_edge(
        START,
        "start_request",
    )

    builder.add_edge(
        "start_request",
        "rewrite",
    )

    builder.add_edge(
        "rewrite",
        "detect_search_intent",
    )

    builder.add_edge(
        "detect_search_intent",
        "detect_freshness",
    )

    builder.add_conditional_edges(
        "detect_freshness",
        after_freshness,
        {
            "search": "search",
            "memory": "retrieve_memory",
        },
    )

    builder.add_edge(
        "retrieve_memory",
        "evaluate_memory",
    )

    builder.add_conditional_edges(
        "evaluate_memory",
        after_memory_evaluation,
        {
            "generate": "generate",
            "search": "search",
        },
    )

    builder.add_conditional_edges(
        "search",
        after_search,
        {
            "extract": "extract",
            "retry_search": "retry_search",
            "fail": "fail",
        },
    )

    builder.add_edge(
        "retry_search",
        "search",
    )

    builder.add_conditional_edges(
        "extract",
        after_extract,
        {
            "chunk": "chunk",
            "fail": "fail",
        },
    )

    builder.add_conditional_edges(
        "chunk",
        after_chunk,
        {
            "retrieve": "retrieve",
            "fail": "fail",
        },
    )

    builder.add_conditional_edges(
        "retrieve",
        after_retrieve,
        {
            "rerank": "rerank",
            "refine": "refine",
        },
    )

    builder.add_conditional_edges(
        "rerank",
        after_rerank,
        {
            "evaluate": "evaluate",
            "refine": "refine",
        },
    )

    builder.add_conditional_edges(
        "evaluate",
        after_evaluation,
        {
            "generate": "generate",
            "refine": "refine",
        },
    )

    builder.add_conditional_edges(
        "refine",
        after_refine,
        {
            "search": "search",
            "generate": "generate",
            "fail": "fail",
        },
    )

    builder.add_conditional_edges(
        "generate",
        after_generate,
        {
            "repair_citations": "repair_citations",
            "end": "finish_request",
        },
    )

    builder.add_conditional_edges(
        "repair_citations",
        after_repair,
        {
            "end": "finish_request",
            "fail": "fail",
        },
    )

    builder.add_edge(
        "finish_request",
        END,
    )

    builder.add_edge(
        "fail",
        END,
    )

    return builder.compile(
        checkpointer=checkpointer,
    )