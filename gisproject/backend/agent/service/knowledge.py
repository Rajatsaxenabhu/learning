from langchain_core.tools import StructuredTool

from agent.rag.retrieval.embeddings import EmbeddingService
from agent.rag.retrieval.vectorstore import VectorStore


def create_knowledge_retriever():

    embeddings = EmbeddingService(mode="http")

    vector_store = VectorStore(
        embeddings=embeddings,
        collection_name="gis_knowledge",
    )

    return vector_store.store.as_retriever(
        search_kwargs={
            "k": 5
        }
    )


def create_knowledge_tool(retriever):

    async def search_knowledge(query: str) -> str:

        documents = await retriever.ainvoke(query)

        if not documents:
            return (
                "No relevant information was found "
                "in the internal GIS knowledge base."
            )

        return "\n\n".join(
            document.page_content
            for document in documents
        )

    tool = StructuredTool.from_function(
        coroutine=search_knowledge,
        name="search_knowledge",
        description=(
            "Search the internal GIS knowledge base.\n\n"
            "Use this for stable GIS knowledge such as:\n"
            "- coordinate reference systems\n"
            "- projections\n"
            "- GIS concepts\n"
            "- remote sensing concepts\n"
            "- spatial analysis concepts\n"
            "- internal GIS documentation\n\n"
            "Do not use this for:\n"
            "- inspecting an uploaded dataset\n"
            "- executing spatial operations\n"
            "- current or latest information"
        ),
    )

    tool.metadata = {
        "read_only": True,
        "source": "qdrant",
    }

    return tool