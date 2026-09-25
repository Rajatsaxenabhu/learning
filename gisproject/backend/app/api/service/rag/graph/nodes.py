from app.api.service.rag.evaluator import RetrievalEvaluator
from app.api.service.rag.refiner import QueryRefiner
from app.api.service.rag.query.reqwiter import QueryRewriter
from app.api.service.rag.retrieval.hybrid import HybridRetriever
from app.api.service.rag.search.validator import CitationValidator

from langgraph.types import interrupt


class RAGNodes:

    def __init__(
        self,
        search_service,
        extractor,
        chunker,
        vector_store,
        bm25_retriever,
        reranker,
        rewriter: QueryRewriter,
        evaluator: RetrievalEvaluator,
        refiner: QueryRefiner,
        llm,
        
    ):
        self.search_service = search_service
        self.extractor = extractor
        self.chunker = chunker
        self.vector_store = vector_store
        self.bm25_retriever = bm25_retriever
        self.reranker = reranker
        self.rewriter = rewriter
        self.evaluator = evaluator
        self.refiner = refiner
        self.llm = llm
        self.citation_validator = CitationValidator()

        self.hybrid_retriever = HybridRetriever(
            vector_store=vector_store,
            bm25_retriever=bm25_retriever,
        )


    async def rewrite(self, state):

        search_query = await self.rewriter.rewrite(
            state["query"]
        )

        return {
            "search_query": search_query,
            "seen_queries": [search_query.strip().lower()],
            "iteration": 0,
            "search_retry_count": 0,
            "status": "rewritten",
        }   
    async def evaluate_memory(self, state):

        documents = state["candidate_documents"]

        if not documents:
            return {
                "retrieval_sufficient": False,
                "missing_information": "No relevant information found.",
                "evaluation_reason": "Qdrant returned no relevant documents.",
                "status": "memory_insufficient",
            }

        evaluation = await self.evaluator.evaluate(
            query=state["query"],
            documents=documents,
        )

        if evaluation["sufficient"]:
            return {
                "retrieved_documents": documents,
                "retrieval_sufficient": True,
                "missing_information": "",
                "evaluation_reason": evaluation["reason"],
                "status": "memory_sufficient",
            }

        return {
            "retrieved_documents": documents,
            "retrieval_sufficient": False,
            "missing_information": evaluation["missing_information"],
            "evaluation_reason": evaluation["reason"],
            "status": "memory_insufficient",
        }

    

    async def search(self, state):

        print("\n🌐 TAVILY SEARCH CALLED")
        print(f"Search query: {state['search_query']}")

        try:

            results = await self.search_service.search(
                state["search_query"]
            )

            if not results:

                return {
                    "search_results": [],
                    "web_search_called": True,
                    "status": "no_search_results",
                }

            return {
                "search_results": results,
                "web_search_called": True,
                "status": "searched",
            }

        except Exception as e:

            print(f"❌ Tavily search failed: {e}")

            return {
                "search_results": [],
                "web_search_called": True,
                "status": "search_failed",
                "errors": [str(e)],
            }


    async def extract(self, state):

        documents = []
        errors = list(state.get("errors", []))

        for result in state["search_results"]:

            url = result.get("url")

            if not url:
                continue

            try:
                document = await self.extractor.extract(url)
                documents.append(document)

            except Exception as exc:

                errors.append(
                    f"Extraction failed for {url}: {exc}"
                )

        return {
            "documents": documents,
            "errors": errors,
            "status": (
                "extracted"
                if documents
                else "extraction_failed"
            ),
        }

    async def chunk(self, state):

        chunks = self.chunker.split(
            state["documents"]
        )

        return {
            "chunks": chunks,
            "status": (
                "chunked"
                if chunks
                else "chunking_failed"
            ),
        }
    async def detect_freshness(self, state):

        prompt = f"""
    Determine whether this query requires
    fresh or current information from the web.

    User query:
    {state["query"]}

    Return ONLY one word:

    FRESH
    or
    STABLE

    Return FRESH when the query asks for information
    that can change over time, including:

    - latest
    - current
    - today
    - yesterday
    - this week
    - this month
    - recent
    - newest
    - recent developments
    - current status
    - current events
    - news
    - updates

    Return STABLE when the query asks for information
    that is generally not time-sensitive.

    Examples:

    "What is EPSG:4326?"
    STABLE

    "What is Web Mercator?"
    STABLE

    "What are the latest NISAR developments?"
    FRESH

    "What is the current status of NISAR?"
    FRESH

    "NISAR news today"
    FRESH
    """

        response = await self.llm.ainvoke(
            prompt
        )

        decision = (
            response.content
            .strip()
            .upper()
        )

        if decision == "FRESH":
            return {
                "freshness_required": True,
                "freshness_reason": "time_sensitive_query",
                "status": "freshness_required",
            }

        return {
            "freshness_required": False,
            "freshness_reason": "",
            "status": "stable_query",
        }
    async def retrieve(self, state):

        if state["chunks"]:

            self.vector_store.add_documents(
                state["chunks"]
            )

            self.bm25_retriever.add_documents(
                state["chunks"]
            )

        candidates = self.hybrid_retriever.search(
            query=state["search_query"],
            k=15,
            fetch_k=15,
        )

        return {
            "candidate_documents": candidates,
            "status": (
                "retrieved"
                if candidates
                else "retrieval_failed"
            ),
        }

    async def rerank(self, state):

        documents = self.reranker.rerank(
            query=state["query"],
            documents=state["candidate_documents"],
            top_k=5,
        )

        return {
            "retrieved_documents": documents,
            "status": (
                "reranked"
                if documents
                else "reranking_failed"
            ),
        }
    async def retry_search(self, state):

        return {
            "search_retry_count": (
                state["search_retry_count"] + 1
            ),
            "status": "retrying_search",
        }
    async def evaluate(self, state):

        evaluation = await self.evaluator.evaluate(
            query=state["query"],
            documents=state["retrieved_documents"],
        )

        return {
            "retrieval_sufficient": evaluation["sufficient"],
            "evaluation_reason": evaluation["reason"],
            "missing_information": evaluation[
                "missing_information"
            ],
            "status": "evaluated",
        }
    async def retrieve_memory(self, state):

        candidates = self.hybrid_retriever.search(
            query=state["search_query"],
            k=10,
            fetch_k=15,
        )

        return {
            "candidate_documents": candidates,
            "status": (
                "memory_retrieved"
                if candidates
                else "memory_retrieval_failed"
            ),
        }
    async def refine(self, state):

        search_query = await self.refiner.refine(
            original_query=state["query"],
            missing_information=state[
                "missing_information"
            ],
        )

        search_query = search_query.strip()

        normalized_query = search_query.lower()

        seen_queries = list(
            state.get("seen_queries", [])
        )

        if normalized_query in seen_queries:
            return {
                "search_query": search_query,
                "status": "duplicate_query",
            }

        seen_queries.append(normalized_query)

        return {
            "search_query": search_query,
            "seen_queries": seen_queries,
            "iteration": state["iteration"] + 1,
            "search_retry_count": 0,
            "status": "refined",
        }

    def after_refine(state):

        if state["status"] == "duplicate_query":
            return "fail"

        if state["iteration"] >= state["max_iterations"]:
            return "generate"

        return "search"

    async def fail(self, state):

        return {
            "answer": (
                "I could not retrieve enough "
                "reliable information to answer "
                "the question."
            ),
            "status": "failed",
        }
    async def detect_search_intent(self, state):

        prompt = f"""
    Determine whether the user explicitly wants
    fresh information from the web.

    User query:
    {state["query"]}

    Return ONLY one of:

    WEB
    MEMORY

    Return WEB if the user explicitly asks to:
    - search the web
    - search online
    - look this up
    - find more information online
    - get current/latest information

    Otherwise return MEMORY.
    """

        response = await self.llm.ainvoke(prompt)

        decision = response.content.strip().upper()

        if decision == "WEB":
            return {
                "force_web_search": True,
                "search_reason": "explicit_user_request",
                "status": "search_required",
            }

        return {
            "force_web_search": False,
            "search_reason": "",
            "status": "memory_search",
        }
  
    async def detect_search_intent(self, state):

        prompt = f"""
    Determine whether the user explicitly wants
    fresh information from the web.

    User query:
    {state["query"]}

    Return ONLY one word:

    WEB
    or
    MEMORY

    Return WEB when the user explicitly asks to:
    - search the web
    - search online
    - look this up
    - find information online
    - find the latest information
    - get current information

    Otherwise return MEMORY.
    """

        response = await self.llm.ainvoke(prompt)

        decision = response.content.strip().upper()

        if decision == "WEB":
            return {
                "force_web_search": True,
                "search_reason": "explicit_user_request",
                "status": "search_required",
            }

        return {
            "force_web_search": False,
            "search_reason": "",
            "status": "memory_search",
        }
    async def repair_citations(self, state):

        sources = state.get("sources", [])
        answer = state.get("answer", "")

        source_context = "\n".join(
            f"[{source['id']}] {source['title']} - {source['source']}"
            for source in sources
        )

        prompt = f"""
    You are a citation repair system.

    The following answer contains invalid citations.

    Answer:

    {answer}

    Valid sources:

    {source_context}

    Rules:

    - Keep the meaning of the answer unchanged.
    - Do not add new facts.
    - Do not use your own knowledge.
    - Only use citation IDs that exist in the sources.
    - Every factual claim must have a valid citation.
    - Return ONLY the corrected answer.
    """

        response = await self.llm.ainvoke(prompt)

        repaired_answer = response.content

        validation = self.citation_validator.validate(
            answer=repaired_answer,
            sources=sources,
        )

        if not validation["valid"]:
            return {
                "answer": repaired_answer,
                "citation_valid": False,
                "invalid_citations": validation["invalid_citations"],
                "status": "citation_repair_failed",
                "errors": [
                    (
                        "Citation repair failed. "
                        f"Invalid citations: "
                        f"{validation['invalid_citations']}"
                    )
                ],
            }

        return {
            "answer": repaired_answer,
            "citation_valid": True,
            "invalid_citations": [],
            "status": "success",
        }

    async def generate(self, state):

        approval = interrupt(
            {
                "type": "generation_approval",
                "message": "Retrieved information is ready. Generate the final answer?",
                "query": state["query"],
                "sources": [
                    {
                        "title": doc.metadata.get("title", ""),
                        "source": doc.metadata.get("source", ""),
                    }
                    for doc in state["retrieved_documents"]
                ],
            }
        )

        if approval != "approve":
            return {
                "answer": "Final answer generation was rejected.",
                "status": "generation_rejected",
            }

        # -----------------------------
        # Build unique sources
        # -----------------------------
        sources = []
        source_id_map = {}

        for doc in state["retrieved_documents"]:

            source = doc.metadata.get("source", "")
            title = doc.metadata.get("title", "")

            if not source:
                continue

            if source not in source_id_map:

                source_id = len(source_id_map) + 1

                source_id_map[source] = source_id

                sources.append(
                    {
                        "id": source_id,
                        "title": title,
                        "source": source,
                    }
                )

        # -----------------------------
        # Build context
        # -----------------------------
        context_parts = []

        for doc in state["retrieved_documents"]:

            source = doc.metadata.get("source", "")
            title = doc.metadata.get("title", "")

            if not source:
                continue

            source_id = source_id_map[source]

            context_parts.append(
                f"""
    SOURCE [{source_id}]
    TITLE: {title}
    URL: {source}

    CONTENT:
    {doc.page_content}
    """
            )

        context = "\n\n".join(context_parts)

        # -----------------------------
        # Generate answer
        # -----------------------------
        prompt = f"""
    You are a helpful web RAG assistant.

    Answer the user's question using ONLY
    the information provided in the sources.

    Every factual claim that comes from a source
    must include an inline citation.

    Citation format:

    [1]
    [2]
    [3]

    Rules:

    - Use ONLY the provided sources.
    - Do not use your own knowledge.
    - Do not invent facts.
    - Do not invent citations.
    - Only use citation IDs that exist in the provided sources.
    - Every important factual claim must have a citation.
    - If multiple sources support a claim, cite all relevant sources.
    - If the sources are insufficient, say so clearly.

    User question:

    {state["query"]}

    Sources:

    {context}
    """

        response = await self.llm.ainvoke(prompt)

        answer = response.content

        # -----------------------------
        # Validate citations
        # -----------------------------
        validation = self.citation_validator.validate(
            answer=answer,
            sources=sources,
        )

        if not validation["valid"]:
            return {
                "answer": answer,
                "sources": sources,
                "citation_valid": False,
                "invalid_citations": validation["invalid_citations"],
                "status": "invalid_citations",
                "errors": [
                    (
                        "Invalid citation IDs generated: "
                        f"{validation['invalid_citations']}"
                    )
                ],
            }

        return {
            "answer": answer,
            "sources": sources,
            "citation_valid": True,
            "invalid_citations": [],
            "status": "success",
        }
