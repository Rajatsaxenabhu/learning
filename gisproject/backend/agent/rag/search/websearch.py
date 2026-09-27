from typing import Any
from tavily import AsyncTavilyClient
from agent.config.rag import TAVILY_API_KEY

class WebSearch:
    def __init__(self):
        self.client = AsyncTavilyClient(
            api_key=TAVILY_API_KEY
        )

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[dict[str, Any]]:

        response = await self.client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
        )

        return response["results"]