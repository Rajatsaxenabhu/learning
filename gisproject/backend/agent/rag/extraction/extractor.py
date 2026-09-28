import anyio

from urllib.parse import urlparse

from bs4 import BeautifulSoup
from langchain_core.documents import Document

from agent.rag.extraction.fetcher.manager import (
    FetchManager,
)


class WebExtractor:

    def __init__(
        self,
        fetch_manager: FetchManager,
        max_concurrency: int = 10,
    ):

        self.fetch_manager = fetch_manager

        self.limiter = anyio.CapacityLimiter(
            max_concurrency
        )

    async def extract(
        self,
        url: str,
    ) -> Document | None:

        result = await self.fetch_manager.fetch(
            url
        )

        if not result.success:
            return None

        content = result.content

        if not content:
            return None

        content_type = (
            result.content_type or ""
        ).lower()

        if not (
            "text/html" in content_type
            or
            "application/xhtml+xml"
            in content_type
        ):
            return None

        try:

            soup = BeautifulSoup(
                content,
                "html.parser",
            )

            title = ""

            if soup.title:

                title = soup.title.get_text(
                    strip=True
                )

            for tag in soup(
                (
                    "script",
                    "style",
                    "nav",
                    "footer",
                    "header",
                )
            ):
                tag.decompose()

            text = soup.get_text(
                separator="\n",
                strip=True,
            )

            if not text:
                return None

        except Exception:
            return None

        final_url = (
            result.final_url
            or url
        )

        domain = urlparse(
            final_url
        ).netloc

        return Document(
            page_content=text,
            metadata={
                "source": url,
                "final_url": final_url,
                "title": title,
                "domain": domain,
                "source_type": "webpage",
                "fetch_method": result.method,
                "status_code": result.status_code,
                "content_type": result.content_type,
            },
        )

    async def extract_concurrent(
        self,
        urls: list[str],
    ) -> list[Document]:

        unique_urls = list(
            dict.fromkeys(
                url
                for url in urls
                if url
            )
        )

        if not unique_urls:
            return []

        documents: list[Document | None] = [
            None
        ] * len(unique_urls)

        async def extract_one(
            index: int,
            url: str,
        ) -> None:

            async with self.limiter:

                documents[index] = (
                    await self.extract(url)
                )

        async with anyio.create_task_group() as tg:

            for index, url in enumerate(
                unique_urls
            ):

                tg.start_soon(
                    extract_one,
                    index,
                    url,
                )

        return [
            document
            for document in documents
            if document is not None
        ]
