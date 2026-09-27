from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class FetchResult:

    url: str
    final_url: str | None

    success: bool

    status_code: int | None

    content: bytes | None

    content_type: str | None

    method: str

    error: str | None = None