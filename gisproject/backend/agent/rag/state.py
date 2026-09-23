from typing import Any

from langchain_core.documents import Document
from typing_extensions import TypedDict


class RAGState(TypedDict):

    query: str

    search_results: list[dict[str, Any]]

    documents: list[Document]

    chunks: list[Document]

    retrieved_documents: list[Document]

    answer: str