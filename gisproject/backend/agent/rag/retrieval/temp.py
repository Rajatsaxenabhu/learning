import httpx
from langchain_core.embeddings import Embeddings


class EmbeddingService(Embeddings):

    def __init__(
        self,
        base_url: str = "http://172.16.32.50:7070",
    ):
        self.base_url = base_url.rstrip("/")

    def embed_documents(
        self,
        documents: list[str],
    ) -> list[list[float]]:

        response = httpx.post(
            f"{self.base_url}/embed",
            json={
                "texts": documents,
            },
            timeout=120.0,
        )

        response.raise_for_status()

        return response.json()["embeddings"]

    def embed_query(
        self,
        query: str,
    ) -> list[float]:

        response = httpx.post(
            f"{self.base_url}/embed",
            json={
                "texts": [query],
            },
            timeout=120.0,
        )

        response.raise_for_status()

        return response.json()["embeddings"][0]

    
embedding = EmbeddingService()

documents = [
    "What is GIS?",
    "What is remote sensing?",
]

vectors = embedding.embed_documents(documents)

print(len(vectors))
print(len(vectors[0]))