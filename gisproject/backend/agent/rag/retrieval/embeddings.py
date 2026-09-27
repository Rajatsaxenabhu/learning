from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingService(Embeddings):

    def __init__(
        self,
        model_name: str = "/home/app/media/models/all-MiniLM-L6-v2",
        device: str = "cuda",
    ):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={
                "device": device,
            },
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