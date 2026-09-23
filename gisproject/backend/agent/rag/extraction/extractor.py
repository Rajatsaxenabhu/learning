from typing import Any
import httpx
from bs4 import BeautifulSoup
from langchain_core.documents import Document

class WebExtractor:

    def __init__(
        self,
        timeout: float = 10.0,
    ):
        self.timeout = timeout

    async def extract(
        self,
        url: str,
    ) -> dict[str, Any]:

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
            ["script", "style", "nav", "footer", "header"]
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

        return Document(
            page_content=content,
            metadata={
                "source": url,
                "title": title,
            },
        )