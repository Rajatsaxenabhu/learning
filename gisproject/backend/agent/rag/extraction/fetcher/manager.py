from agent.rag.extraction.fetcher.browser import (
    BrowserFetcher,
)
from agent.rag.extraction.fetcher.http import (
    HTTPFetcher,
)
from agent.rag.extraction.models import FetchResult
from agent.rag.extraction.fetcher.validator import (
    ContentValidator,
)


class FetchManager:

    def __init__(
        self,
        http_fetcher: HTTPFetcher,
        browser_fetcher: BrowserFetcher,
        validator: ContentValidator,
    ):

        self.http_fetcher = http_fetcher
        self.browser_fetcher = browser_fetcher
        self.validator = validator

    async def start(self):

        await self.http_fetcher.start()
        await self.browser_fetcher.start()

    async def close(self):

        await self.http_fetcher.close()
        await self.browser_fetcher.close()

    async def fetch(
        self,
        url: str,
    ) -> FetchResult:

        http_result = (
            await self.http_fetcher.fetch(url)
        )

        if http_result.success:

            validation = self.validator.validate(
                content=http_result.content,
                content_type=http_result.content_type,
            )

            if validation.valid:
                return http_result

            if self._should_use_browser_for_content(
                validation.reason
            ):

                return await self.browser_fetcher.fetch(
                    url
                )

            return FetchResult(
                url=http_result.url,
                final_url=http_result.final_url,
                success=False,
                status_code=http_result.status_code,
                content=http_result.content,
                content_type=http_result.content_type,
                method=http_result.method,
                error=validation.reason,
            )

        if self._should_use_browser(
            http_result
        ):

            return await self.browser_fetcher.fetch(
                url
            )

        return http_result

    def _should_use_browser(
        self,
        result: FetchResult,
    ) -> bool:

        if result.status_code in {
            401,
            403,
            406,
        }:
            return True

        if result.status_code in {
            500,
            502,
            503,
            504,
        }:
            return True

        if result.error in {
            "request_timeout",
        }:
            return True

        return False

    def _should_use_browser_for_content(
        self,
        reason: str,
    ) -> bool:

        return reason in {
            "challenge_page",
            "content_too_short",
            "boilerplate_content",
        }