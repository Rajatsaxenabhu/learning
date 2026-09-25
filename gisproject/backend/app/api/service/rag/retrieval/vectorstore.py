from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


class VectorStore:

    def __init__(
        self,
        embeddings,
        collection_name: str = "web_rag",
        url: str = "http://localhost:6333",
    ):

        self.client = QdrantClient(
            url=url,
        )

        self.collection_name = collection_name

        if not self.client.collection_exists(
            collection_name
        ):
            vector_size = len(
                embeddings.embed_query("test")
            )

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

        self.store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=embeddings,
        )

    def add_documents(
        self,
        documents: list[Document],
    ):
        if not documents:
            return

        self.store.add_documents(
            documents
        )

    def search(
        self,
        query: str,
        k: int = 5,
    ):
        return self.store.similarity_search(
            query,
            k=k,
        )

    def get_documents(
        self,
        limit: int = 10000,
    ) -> list[Document]:

        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        documents = []

        for point in points:

            payload = point.payload or {}

            page_content = payload.get(
                "page_content",
                "",
            )

            metadata = payload.get(
                "metadata",
                {},
            )

            if not page_content:
                continue

            documents.append(
                Document(
                    page_content=page_content,
                    metadata=metadata,
                )
            )

        return documents