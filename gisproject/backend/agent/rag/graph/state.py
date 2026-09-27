from typing import Any
from langchain_core.documents import Document
from typing_extensions import TypedDict


class RAGState(TypedDict):

    query: str
    search_query: str
    seen_queries: list[str]

    search_results: list[dict[str, Any]]

    documents: list[Document]
    chunks: list[Document]

    candidate_documents: list[Document]
    retrieved_documents: list[Document]

    sources: list[dict[str, Any]]

    missing_information: str
    evaluation_reason: str
    retrieval_sufficient: bool

    citation_valid: bool
    invalid_citations: list[str]

    iteration: int
    max_iterations: int

    search_retry_count: int
    max_search_retries: int

    cache_hit: bool

    force_web_search: bool
    search_reason: str
    web_search_called: bool

    freshness_required: bool
    freshness_reason: str

    metrics: dict[str, Any]

    status: str
    answer: str

    errors: list[str]