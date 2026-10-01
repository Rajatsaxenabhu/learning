
from typing import Any

from langgraph.types import Command

from agent.llm.model import model

from agent.rag.search.websearch import WebSearch

from agent.rag.extraction.fetcher import (
    BrowserFetcher,
    HTTPFetcher,
    FetchManager,
    ContentValidator,
)

from agent.rag.extraction.extractor import (
    WebExtractor,
)

from agent.rag.retrieval.chunker import WebChunker
from agent.rag.retrieval.embeddings import EmbeddingService
from agent.rag.retrieval.vectorstore import VectorStore
from agent.rag.retrieval.bm25 import BM25Retriever
from agent.rag.retrieval.reranker import Reranker

from agent.rag.query.reqwiter import QueryRewriter
from agent.rag.evaluator import RetrievalEvaluator
from agent.rag.refiner import QueryRefiner
from agent.rag.graph.graph import build_rag_graph


class WebRAG:

    def __init__(
        self,
        collection_name: str = "web_rag_test",
        qdrant_url: str = "http://qdrant:6333",
        checkpointer=None,
    ):

        self.collection_name = collection_name
        self.qdrant_url = qdrant_url
        self.checkpointer = checkpointer

        self.graph = None
        self.initialized = False

        self.search_service = None

        self.http_fetcher = None
        self.browser_fetcher = None
        self.fetch_manager = None
        self.content_validator = None

        self.extractor = None
        self.chunker = None
        self.embedding_service = None
        self.vector_store = None
        self.bm25_retriever = None
        self.reranker = None
        self.rewriter = None
        self.evaluator = None
        self.refiner = None

    async def initialize(self):

        if self.initialized:
            return self

        self.search_service = WebSearch()

        self.http_fetcher = HTTPFetcher()

        self.browser_fetcher = BrowserFetcher()

        self.content_validator = ContentValidator()

        self.fetch_manager = FetchManager(
            http_fetcher=self.http_fetcher,
            browser_fetcher=self.browser_fetcher,
            validator=self.content_validator,
        )

        await self.fetch_manager.start()

        self.extractor = WebExtractor(
            fetch_manager=self.fetch_manager,
        )

        self.chunker = WebChunker(
            chunk_size=1000,
            chunk_overlap=150,
        )

        self.embedding_service = EmbeddingService(mode="local")

        self.vector_store = VectorStore(
            embeddings=self.embedding_service.embeddings,
            collection_name=self.collection_name,
            url=self.qdrant_url,
        )

        self.bm25_retriever = BM25Retriever()

        self.reranker = Reranker(
            mode="local"
        )

        self.rewriter = QueryRewriter(
            llm=model,
        )

        self.evaluator = RetrievalEvaluator(
            llm=model,
        )

        self.refiner = QueryRefiner(
            llm=model,
        )

        documents = self.vector_store.get_documents()

        self.bm25_retriever.add_documents(
            documents
        )

        self.graph = build_rag_graph(
            search_service=self.search_service,
            extractor=self.extractor,
            chunker=self.chunker,
            vector_store=self.vector_store,
            bm25_retriever=self.bm25_retriever,
            reranker=self.reranker,
            rewriter=self.rewriter,
            evaluator=self.evaluator,
            refiner=self.refiner,
            llm=model,
            checkpointer=self.checkpointer,
        )

        self.initialized = True

        return self

    def get_graph(self):

        if not self.initialized:
            raise RuntimeError(
                "WebRAG is not initialized"
            )

        return self.graph

    def _initial_state(
        self,
        query: str,
    ) -> dict[str, Any]:

        return {
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

    def _config(
        self,
        thread_id: str,
    ) -> dict[str, Any]:

        return {
            "configurable": {
                "thread_id": thread_id,
            }
        }

    async def query(
        self,
        query: str,
        thread_id: str,
    ) -> dict[str, Any]:

        if not self.initialized:
            raise RuntimeError(
                "WebRAG is not initialized"
            )

        config = self._config(
            thread_id
        )

        await self.graph.ainvoke(
            self._initial_state(query),
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

        if not self.initialized:
            raise RuntimeError(
                "WebRAG is not initialized"
            )

        config = self._config(
            thread_id
        )

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

        if not self.initialized:
            raise RuntimeError(
                "WebRAG is not initialized"
            )

        config = self._config(
            thread_id
        )

        state = await self.graph.aget_state(
            config
        )

        values = state.values

       
        return {
            "answer": values.get(
                "answer",
                "",
            ),
            "sources": values.get(
                "sources",
                [],
            ),
            "status": values.get(
                "status",
                "",
            ),
            "metrics": values.get(
                "metrics",
                {},
            ),
            "errors": values.get(
                "errors",
                [],
            ),
            "tasks": state.tasks,
            "thread_id": thread_id,
        }

    async def close(self):

        if not self.initialized:
            return

        if self.fetch_manager is not None:

            await self.fetch_manager.close()

        self.graph = None

        self.search_service = None

        self.http_fetcher = None
        self.browser_fetcher = None
        self.fetch_manager = None
        self.content_validator = None

        self.extractor = None
        self.chunker = None
        self.embedding_service = None
        self.vector_store = None
        self.bm25_retriever = None
        self.reranker = None
        self.rewriter = None
        self.evaluator = None
        self.refiner = None

        self.initialized = False
