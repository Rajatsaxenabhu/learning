from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


class VectorStore:

    def __init__(
        self,
        embeddings: Embeddings,
        collection_name: str = "web_rag",
        url: str = "http://qdrant:6333",
    ):
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name
        self.embeddings = embeddings

        self._create_collection_if_not_exists()

        self.store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )

    def _create_collection_if_not_exists(self):
        if self.client.collection_exists(
            self.collection_name
        ):
            return

        vector_size = len(
            self.embeddings.embed_query("test")
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

    def add_documents(
        self,
        documents: list[Document],
        batch_size: int = 64,
    ):
        if not documents:
            return

        for start in range(0, len(documents), batch_size):
            batch = documents[
                start:start + batch_size
            ]

            self.store.add_documents(batch)

    def search(
        self,
        query: str,
        k: int = 5,
    ) -> list[Document]:

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