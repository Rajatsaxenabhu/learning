import httpx

from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings


class HTTPEmbeddings(Embeddings):

    def __init__(
        self,
        base_url: str,
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


class EmbeddingService(Embeddings):

    def __init__(
        self,
        mode: str = "local",
        model_name: str = "/home/app/media/models/bge-large-en-v1.5",
        device: str = "cuda",
        base_url: str = "http://172.16.32.50:7070",
    ):
        if mode == "local":

            self.embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={
                    "device": device,
                },
            )

        elif mode == "http":

            self.embeddings = HTTPEmbeddings(
                base_url=base_url,
            )

        else:

            raise ValueError(
                f"Unsupported embedding mode: {mode}"
            )

    def embed_documents(
        self,
        documents: list[str],
    ) -> list[list[float]]:

        return self.embeddings.embed_documents(
            documents
        )

    def embed_query(
        self,
        query: str,
    ) -> list[float]:

        return self.embeddings.embed_query(
            query
        )