from langgraph.graph import StateGraph, START, END
from agent.rag.state import RAGState
from agent.rag.search.websearch import WebSearch
from agent.rag.extraction.extractor import WebExtractor
from agent.rag.retrieval.chunker import WebChunker
from agent.rag.retrieval.vectorstore import VectorStore

def make_search_node(search_service: WebSearch):

    async def search_node(state: RAGState):

        query = state["query"]

        results = await search_service.search(
            query=query,
            max_results=5,
        )

        return {
            "search_results": results
        }

    return search_node

def make_extraction_node(extractor):

    async def extraction_node(state: RAGState):

        documents = []

        for result in state["search_results"]:

            url = result.get("url")

            if not url:
                continue

            try:
                document = await extractor.extract(url)
                documents.append(document)

            except Exception as exc:
                print(
                    f"Failed to extract {url}: {exc}"
                )

        return {
            "documents": documents
        }

    return extraction_node

async def retrieve_node(state: RAGState):
    search_results = state["search_results"]

    print(f"RETRIEVE: {len(search_results)} results")

    # Temporary implementation.
    # Real content extraction/retrieval comes later.
    documents = search_results

    return {
        "documents": documents
    }

def make_chunking_node(chunker):

    async def chunking_node(state: RAGState):

        chunks = chunker.split(
            state["documents"]
        )

        return {
            "chunks": chunks
        }

    return chunking_node
def make_retrieval_node(vector_store):

    async def retrieval_node(state: RAGState):

        query = state["query"]

        documents = vector_store.search(
            query=query,
            k=5,
        )

        return {
            "retrieved_documents": documents
        }

    return retrieval_node

def make_index_node(vector_store):

    async def index_node(state: RAGState):

        chunks = state["chunks"]

        if chunks:
            vector_store.add_documents(
                chunks
            )

        return {}

    return index_node

def make_generate_node(llm):

    async def generate_node(state: RAGState):
        query = state["query"]
        retrieved_documents = state["retrieved_documents"]

        print(f"GENERATE: {query}")

        context = "\n\n".join(
            doc.page_content for doc in retrieved_documents
        )

        prompt = (
            "Answer the question using only the context below. "
            "If the context doesn't contain the answer, say so.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}"
        )

        response = await llm.ainvoke(prompt)

        return {
            "answer": response.content
        }

    return generate_node

def build_graph(search_service: WebSearch, extractor: WebExtractor, chunker: WebChunker, vector_store: VectorStore, llm):

    builder = StateGraph(RAGState)

    builder.add_node(
        "search",
        make_search_node(search_service),
    )

    builder.add_node(
        "extract",
        make_extraction_node(extractor),
    )

    builder.add_node(
        "chunk",
        make_chunking_node(chunker),
    )

    builder.add_node(
        "index",
        make_index_node(vector_store),
    )

    builder.add_node(
        "retrieve",
        make_retrieval_node(vector_store),
    )

    builder.add_node(
        "generate",
        make_generate_node(llm),
    )

    builder.add_edge(START, "search")
    builder.add_edge("search", "extract")
    builder.add_edge("extract", "chunk")
    builder.add_edge("chunk", "index")
    builder.add_edge("index", "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)

    return builder.compile()