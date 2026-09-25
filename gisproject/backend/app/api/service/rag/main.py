import asyncio

from langchain_core.documents import Document

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command

from agent.llm.model import dev_model

from app.api.service.rag.search.websearch import WebSearch
from app.api.service.rag.extraction.extractor import WebExtractor
from app.api.service.rag.retrieval.chunker import WebChunker
from app.api.service.rag.retrieval.embeddings import EmbeddingService
from app.api.service.rag.retrieval.vectorstore import VectorStore
from app.api.service.rag.retrieval.bm25 import BM25Retriever
from app.api.service.rag.retrieval.reranker import Reranker
from app.api.service.rag.query.reqwiter import QueryRewriter
from app.api.service.rag.evaluator import RetrievalEvaluator
from app.api.service.rag.refiner import QueryRefiner
from app.api.service.rag.graph.graph import build_rag_graph


async def main():

    search_service = WebSearch()

    extractor = WebExtractor()

    chunker = WebChunker(
        chunk_size=1000,
        chunk_overlap=150,
    )

    embedding_service = EmbeddingService()

    vector_store = VectorStore(
        embeddings=embedding_service.embeddings,
        collection_name="web_rag_test",
        url="http://localhost:6333",
    )

    bm25_retriever = BM25Retriever()

    reranker = Reranker(
        model_name="BAAI/bge-reranker-base",
    )

    rewriter = QueryRewriter(
        llm=dev_model,
    )

    evaluator = RetrievalEvaluator(
        llm=dev_model,
    )

    refiner = QueryRefiner(
        llm=dev_model,
    )

    documents = [
        Document(
            page_content="""
            EPSG:4326 is the WGS 84 geographic coordinate
            reference system. It uses latitude and longitude
            in degrees.
            """,
            metadata={
                "source": "test-memory",
                "title": "CRS information",
            },
        ),
        Document(
            page_content="""
            EPSG:3857 is the Web Mercator projected
            coordinate reference system. It uses metres
            as projected X and Y coordinates and is widely
            used for web mapping.
            """,
            metadata={
                "source": "test-memory",
                "title": "Web Mercator information",
            },
        ),
    ]

    documents = vector_store.get_documents()
    documents = vector_store.get_documents()

    print(
        "Loaded documents:",
        len(documents),
    )
    bm25_retriever.add_documents(
        documents
    )

    query = "What are the latest developments in NISAR?"

    initial_state = {
        "query": query,
        "search_query": "",
        "seen_queries": [],

        "search_results": [],

        "documents": [],
        "chunks": [],

        "candidate_documents": [],
        "retrieved_documents": [],

        "sources": [],

        "missing_information": "",
        "evaluation_reason": "",
        "retrieval_sufficient": False,

        "citation_valid": False,
        "invalid_citations": [],

        "iteration": 0,
        "max_iterations": 3,

        "search_retry_count": 0,
        "max_search_retries": 2,

        "cache_hit": False,

        "force_web_search": False,
        "search_reason": "",
        "web_search_called": False,

        "freshness_required": False,
        "freshness_reason": "",

        "status": "started",
        "answer": "",

        "errors": [],
    }

    async with AsyncSqliteSaver.from_conn_string(
        "rag_checkpoints.db"
    ) as checkpointer:

        graph = build_rag_graph(
            search_service=search_service,
            extractor=extractor,
            chunker=chunker,
            vector_store=vector_store,
            bm25_retriever=bm25_retriever,
            reranker=reranker,
            rewriter=rewriter,
            evaluator=evaluator,
            refiner=refiner,
            llm=dev_model,
            checkpointer=checkpointer,
        )

        config = {
            "configurable": {
                "thread_id": "rag-9-2-test"
            }
        }

        result = await graph.ainvoke(
            initial_state,
            config=config,
        )

        state = await graph.aget_state(
            config
        )

        print("\n==============================")
        print("RAG 9.2 TEST")
        print("==============================")

        print(
            "Tavily called:",
            state.values.get(
                "web_search_called",
                False,
            ),
        )

        print(
            "Status:",
            state.values.get(
                "status",
                "",
            ),
        )

        print(
            "Candidate documents:",
            len(
                state.values.get(
                    "candidate_documents",
                    [],
                )
            ),
        )

        print("\n==============================")
        print("TASKS")
        print("==============================")

        print(state.tasks)

        if state.tasks:

            result = await graph.ainvoke(
                Command(resume="approve"),
                config=config,
            )

        print("\n==============================")
        print("ANSWER")
        print("==============================")

        print(
            result.get(
                "answer",
                "",
            )
        )

        print("\n==============================")
        print("STATUS")
        print("==============================")

        print(
            result.get(
                "status",
                "",
            )
        )

        if result.get("errors"):

            print("\n==============================")
            print("ERRORS")
            print("==============================")

            for error in result["errors"]:
                print(error)


if __name__ == "__main__":
    asyncio.run(main())