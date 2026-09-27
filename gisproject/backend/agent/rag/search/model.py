from dataclasses import dataclass


@dataclass(slots=True)
class SearchResult:

    url: str

    title: str

    snippet: str

    domain: str | None = None