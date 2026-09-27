from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from agent.rag.extraction.models import FetchResult


class BrowserFetcher:

    def __init__(
        self,
        navigation_timeout: float = 20.0,
        wait_until: str = "domcontentloaded",
    ):

        self.navigation_timeout = navigation_timeout
        self.wait_until = wait_until

        self.playwright: Playwright | None = None
        self.browser: Browser | None = None

    async def start(self):

        if self.browser is not None:
            return

        self.playwright = (
            await async_playwright().start()
        )

        self.browser = await (
            self.playwright.chromium.launch(
                headless=True,
            )
        )

    async def close(self):

        if self.browser is not None:

            await self.browser.close()

            self.browser = None

        if self.playwright is not None:

            await self.playwright.stop()

            self.playwright = None

    async def _create_context(
        self,
    ) -> BrowserContext:

        if self.browser is None:

            raise RuntimeError(
                "BrowserFetcher is not started. "
                "Call await start() first."
            )

        return await self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 "
                "(X11; Linux x86_64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/154.0.0.0 "
                "Safari/537.36"
            ),
            locale="en-US",
            viewport={
                "width": 1440,
                "height": 900,
            },
            java_script_enabled=True,
        )

    async def fetch(
        self,
        url: str,
    ) -> FetchResult:

        if self.browser is None:

            raise RuntimeError(
                "BrowserFetcher is not started. "
                "Call await start() first."
            )

        context: BrowserContext | None = None
        page: Page | None = None

        try:

            context = await self._create_context()

            page = await context.new_page()

            page.set_default_navigation_timeout(
                self.navigation_timeout * 1000
            )

            response = await page.goto(
                url,
                wait_until=self.wait_until,
            )

            if response is None:

                return FetchResult(
                    url=url,
                    final_url=page.url,
                    success=False,
                    status_code=None,
                    content=None,
                    content_type=None,
                    method="browser",
                    error="browser_navigation_failed",
                )

            status_code = response.status

            headers = await response.all_headers()

            content_type = headers.get(
                "content-type"
            )

            content = await page.content()

            success = (
                200 <= status_code < 400
            )

            return FetchResult(
                url=url,
                final_url=page.url,
                success=success,
                status_code=status_code,
                content=content.encode(
                    "utf-8"
                ),
                content_type=content_type,
                method="browser",
                error=(
                    None
                    if success
                    else (
                        f"Browser navigation "
                        f"returned HTTP "
                        f"{status_code}"
                    )
                ),
            )

        except PlaywrightTimeoutError:

            return FetchResult(
                url=url,
                final_url=(
                    page.url
                    if page is not None
                    else None
                ),
                success=False,
                status_code=None,
                content=None,
                content_type=None,
                method="browser",
                error="browser_timeout",
            )

        except Exception as e:

            return FetchResult(
                url=url,
                final_url=(
                    page.url
                    if page is not None
                    else None
                ),
                success=False,
                status_code=None,
                content=None,
                content_type=None,
                method="browser",
                error=str(e),
            )

        finally:

            if page is not None:
                await page.close()

            if context is not None:
                await context.close()