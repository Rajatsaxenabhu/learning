import httpx

from agent.rag.extraction.models import FetchResult


class HTTPFetcher:

    def __init__(
        self,
        timeout: float = 15.0,
        max_redirects: int = 5,
    ):

        self.timeout = httpx.Timeout(
            connect=5.0,
            read=timeout,
            write=timeout,
            pool=5.0,
        )

        self.max_redirects = max_redirects

        self.client: httpx.AsyncClient | None = None

    async def start(self):

        if self.client is not None:
            return

        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            max_redirects=self.max_redirects,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(compatible; WebRAG/1.0; +https://example.com/bot)"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "text/plain;q=0.8,*/*;q=0.5"
                ),
                "Accept-Language": (
                    "en-US,en;q=0.9"
                ),
                "Accept-Encoding": (
                    "gzip, deflate, br"
                ),
                "Connection": "keep-alive",
            },
        )

    async def close(self):

        if self.client is None:
            return

        await self.client.aclose()

        self.client = None

    async def fetch(
        self,
        url: str,
    ) -> FetchResult:

        if self.client is None:
            raise RuntimeError(
                "HTTPFetcher is not started. "
                "Call await start() first."
            )

        try:

            response = await self.client.get(
                url,
            )

            content_type = response.headers.get(
                "content-type"
            )

            success = (
                response.status_code == 200
            )

            return FetchResult(
                url=url,
                final_url=str(response.url),
                success=success,
                status_code=response.status_code,
                content=response.content,
                content_type=content_type,
                method="http",
                error=(
                    None
                    if success
                    else (
                        f"HTTP request failed "
                        f"with status "
                        f"{response.status_code}"
                    )
                ),
            )

        except httpx.TimeoutException:

            return FetchResult(
                url=url,
                final_url=None,
                success=False,
                status_code=None,
                content=None,
                content_type=None,
                method="http",
                error="request_timeout",
            )

        except httpx.HTTPError as e:

            return FetchResult(
                url=url,
                final_url=None,
                success=False,
                status_code=None,
                content=None,
                content_type=None,
                method="http",
                error=str(e),
            )

        except Exception as e:

            return FetchResult(
                url=url,
                final_url=None,
                success=False,
                status_code=None,
                content=None,
                content_type=None,
                method="http",
                error=str(e),
            )