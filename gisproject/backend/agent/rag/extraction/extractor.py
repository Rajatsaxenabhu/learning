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
    ):

        self.fetch_manager = fetch_manager

    async def extract(
        self,
        url: str,
    ) -> Document | None:

        result = await self.fetch_manager.fetch(url)

        if not result.success:
            print(
                f"⚠️ Web extraction failed: "
                f"url={url} "
                f"status={result.status_code} "
                f"error={result.error}"
            )

            return None

        if not result.content:
            return None

        if not result.content_type:
            return None

        if (
            "text/html"
            not in result.content_type.lower()
            and
            "application/xhtml+xml"
            not in result.content_type.lower()
        ):
            print(
                f"⚠️ Unsupported content type: "
                f"{result.content_type} "
                f"url={url}"
            )

            return None

        try:

            soup = BeautifulSoup(
                result.content,
                "html.parser",
            )

            title = (
                soup.title.get_text(
                    strip=True
                )
                if soup.title
                else ""
            )

            for tag in soup(
                [
                    "script",
                    "style",
                    "nav",
                    "footer",
                    "header",
                ]
            ):
                tag.decompose()

            content = soup.get_text(
                separator="\n",
                strip=True,
            )

            if not content:
                return None

            final_url = (
                result.final_url
                or url
            )

            parsed_url = urlparse(
                final_url
            )

            domain = parsed_url.netloc

            return Document(
                page_content=content,
                metadata={
                    "source": url,
                    "final_url": final_url,
                    "title": title,
                    "domain": domain,
                    "source_type": "webpage",
                    "fetch_method": result.method,
                    "status_code": result.status_code,
                    "content_type": result.content_type,
                }
            )

        except Exception as e:

            print(
                f"⚠️ HTML extraction failed "
                f"for {url}: {e}"
            )

            return None