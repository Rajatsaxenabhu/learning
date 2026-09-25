from urllib.parse import urlparse

from bs4 import BeautifulSoup
from langchain_core.documents import Document
import httpx


class WebExtractor:

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    async def extract(self, url: str) -> Document:

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(compatible; WebRAG/1.0)"
                )
            },
        ) as client:

            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
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

        title = (
            soup.title.get_text(strip=True)
            if soup.title
            else ""
        )

        parsed_url = urlparse(url)

        domain = parsed_url.netloc

        return Document(
            page_content=content,
            metadata={
                "source": url,
                "title": title,
                "domain": domain,
            },
        )