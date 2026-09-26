from typing import Any

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


class WebRAG:

    def __init__(
        self,
        checkpoint_path: str = "rag_checkpoints.db",
        collection_name: str = "web_rag_test",
        qdrant_url: str = "http://localhost:6333",
    ):
        self.checkpoint_path = checkpoint_path
        self.collection_name = collection_name
        self.qdrant_url = qdrant_url

        self.checkpointer = None
        self.checkpointer_context = None
        self.graph = None

    async def initialize(self):

        self.checkpointer_context = (
            AsyncSqliteSaver.from_conn_string(
                self.checkpoint_path
            )
        )

        self.checkpointer = (
            await self.checkpointer_context.__aenter__()
        )

        search_service = WebSearch()

        extractor = WebExtractor()

        chunker = WebChunker(
            chunk_size=1000,
            chunk_overlap=150,
        )

        embedding_service = EmbeddingService()

        vector_store = VectorStore(
            embeddings=embedding_service.embeddings,
            collection_name=self.collection_name,
            url=self.qdrant_url,
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

        documents = vector_store.get_documents()

        bm25_retriever.add_documents(
            documents
        )

        self.graph = build_rag_graph(
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
            checkpointer=self.checkpointer,
        )

        return self

    async def query(
        self,
        query: str,
        thread_id: str,
    ) -> dict[str, Any]:

        if self.graph is None:
            raise RuntimeError(
                "WebRAG is not initialized"
            )

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
            "metrics": {},
            "status": "started",
            "answer": "",
            "errors": [],
        }

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        await self.graph.ainvoke(
            initial_state,
            config=config,
        )

        return await self.get_state(
            thread_id
        )

    async def resume(
        self,
        thread_id: str,
        value: Any,
    ) -> dict[str, Any]:

        if self.graph is None:
            raise RuntimeError(
                "WebRAG is not initialized"
            )

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        await self.graph.ainvoke(
            Command(resume=value),
            config=config,
        )

        return await self.get_state(
            thread_id
        )

    async def get_state(
        self,
        thread_id: str,
    ) -> dict[str, Any]:

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        state = await self.graph.aget_state(
            config
        )

        return {
            "answer": state.values.get(
                "answer",
                "",
            ),
            "sources": state.values.get(
                "sources",
                [],
            ),
            "status": state.values.get(
                "status",
                "",
            ),
            "metrics": state.values.get(
                "metrics",
                {},
            ),
            "errors": state.values.get(
                "errors",
                [],
            ),
            "tasks": state.tasks,
            "thread_id": thread_id,
        }

    async def close(self):

        if self.checkpointer_context is not None:

            await self.checkpointer_context.__aexit__(
                None,
                None,
                None,
            )

            self.checkpointer_context = None
            self.checkpointer = None