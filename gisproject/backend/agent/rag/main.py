import asyncio

from agent.rag.graph import build_graph
from agent.rag.search.websearch import WebSearch
from agent.rag.extraction.extractor import WebExtractor
from agent.rag.retrieval.chunker import WebChunker
from agent.rag.retrieval.embeddings import EmbeddingService
from agent.rag.retrieval.vectorstore import VectorStore
from agent.llm.model import model


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
        collection_name="web_rag",
        url="http://localhost:6333",
    )

    graph = build_graph(
        search_service=search_service,
        extractor=extractor,
        chunker=chunker,
        vector_store=vector_store,
        llm=model,
    )
    result = await graph.ainvoke(
        {
            "query": "give details of Sundar Pichai",
            "search_results": [],
            "documents": [],
            "chunks": [],
            "retrieved_documents": [],
            "answer": "",
        }
    )

    print("\n==============================")
    print("RAG RESULT")
    print("==============================")

    print("\nDOCUMENTS:", len(result["documents"]))
    print("CHUNKS:", len(result["chunks"]))
    print(
        "RETRIEVED:",
        len(result["retrieved_documents"]),
    )

    for i, doc in enumerate(
        result["retrieved_documents"]
    ):
        print(f"\n--- RETRIEVED {i} ---")

        print(
            doc.page_content[:500]
        )

        print(
            "SOURCE:",
            doc.metadata.get("source"),
        )

        print(
            "TITLE:",
            doc.metadata.get("title"),
        )
    print("\n==============================")
    print("ANSWER")
    print("==============================")

    print(result["answer"])


if __name__ == "__main__":
    asyncio.run(main())