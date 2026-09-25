from langchain_core.documents import Document


class HybridRetriever:

    def __init__(
        self,
        vector_store,
        bm25_retriever,
    ):
        self.vector_store = vector_store
        self.bm25_retriever = bm25_retriever

    def search(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 10,
    ) -> list[Document]:

        dense_docs = self.vector_store.search(
            query=query,
            k=fetch_k,
        )

        bm25_docs = self.bm25_retriever.search(
            query=query,
            k=fetch_k,
        )

        return self._rrf(
            dense_docs=dense_docs,
            bm25_docs=bm25_docs,
            k=k,
        )

    def _rrf(
        self,
        dense_docs: list[Document],
        bm25_docs: list[Document],
        k: int,
        rrf_k: int = 60,
    ):

        scores = {}
        documents = {}

        for rank, doc in enumerate(
            dense_docs,
            start=1,
        ):
            key = self._document_key(doc)

            scores[key] = (
                scores.get(key, 0.0)
                + 1.0 / (rrf_k + rank)
            )

            documents[key] = doc

        for rank, doc in enumerate(
            bm25_docs,
            start=1,
        ):
            key = self._document_key(doc)

            scores[key] = (
                scores.get(key, 0.0)
                + 1.0 / (rrf_k + rank)
            )

            documents[key] = doc

        ranked_keys = sorted(
            scores,
            key=scores.get,
            reverse=True,
        )

        results = []

        for key in ranked_keys[:k]:
            doc = documents[key]

            doc.metadata["rrf_score"] = scores[key]

            results.append(doc)

        return results

    @staticmethod
    def _document_key(
        doc: Document,
    ):

        source = doc.metadata.get(
            "source",
            "",
        )

        content = doc.page_content.strip()

        return (
            source,
            content[:300],
        )