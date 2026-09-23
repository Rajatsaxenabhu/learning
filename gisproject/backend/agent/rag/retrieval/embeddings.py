from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingService:

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
        )

    def embed_documents(self, documents):
        return self.embeddings.embed_documents(
            documents
        )

    def embed_query(self, query: str):
        return self.embeddings.embed_query(query)