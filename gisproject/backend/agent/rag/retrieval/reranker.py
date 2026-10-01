import httpx

from langchain_core.documents import Document
from sentence_transformers import CrossEncoder


class Reranker:
    def __init__(
        self,
        mode: str = "local",
        model_name: str = "/home/app/media/models/bge-reranker-base",
        device: str = "cuda",
        base_url: str = "http://172.16.32.50:7070",
    ):
        if mode not in ("local", "http"):
            raise ValueError(
                f"Unsupported reranker mode: {mode}"
            )

        self.mode = mode

        if mode == "local":

            self.model = CrossEncoder(
                model_name,
                device=device,
            )

        else:

            self.base_url = base_url.rstrip("/")

    def rerank(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 5,
    ) -> list[Document]:
        if not documents:
            return []

        if self.mode == "local":
            return self._rerank_local(query, documents, top_k)

        return self._rerank_http(query, documents, top_k)

    def _rerank_local(
        self,
        query: str,
        documents: list[Document],
        top_k: int,
    ) -> list[Document]:
        pairs = [
            (query, document.page_content)
            for document in documents
        ]

        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(documents, scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        results = []

        for document, score in ranked[:top_k]:
            document.metadata["rerank_score"] = float(score)
            results.append(document)

        return results

    def _rerank_http(
        self,
        query: str,
        documents: list[Document],
        top_k: int,
    ) -> list[Document]:
        response = httpx.post(
            f"{self.base_url}/rerank",
            json={
                "query": query,
                "documents": [document.page_content for document in documents],
                "top_k": top_k,
            },
            timeout=120.0,
        )

        response.raise_for_status()

        results = response.json()["results"]

        ranked_documents = []

        for result in results:
            document = documents[result["index"]]
            document.metadata["rerank_score"] = result["score"]
            ranked_documents.append(document)

        return ranked_documents
