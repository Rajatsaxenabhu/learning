from langchain_core.documents import Document
from rank_bm25 import BM25Okapi


class BM25Retriever:

    def __init__(self):
        self.documents: list[Document] = []
        self.bm25: BM25Okapi | None = None

    def add_documents(
        self,
        documents: list[Document],
    ):
        if not documents:
            return

        self.documents.extend(documents)

    def set_documents(
        self,
        documents: list[Document],
    ):
        self.documents = list(documents)
        self.build()

    def build(self):
        if not self.documents:
            self.bm25 = None
            return

        tokenized_documents = [
            doc.page_content.lower().split()
            for doc in self.documents
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

    def clear(self):
        self.documents.clear()
        self.bm25 = None

    def search(
        self,
        query: str,
        k: int = 5,
    ) -> list[Document]:

        if self.bm25 is None:
            return []

        tokens = query.lower().split()

        return self.bm25.get_top_n(
            tokens,
            self.documents,
            n=k,
        )
