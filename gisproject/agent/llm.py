from collections.abc import AsyncGenerator
from typing import Any

from openai import AsyncOpenAI


class LLMClient:

    def __init__(
        self,
        model: str = "qwen3-8b",
        host: str = "http://localhost:8010/v1",
    ):
        self.model = model
        self._client = AsyncOpenAI(base_url=host, api_key="EMPTY")

    async def chat_once(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 4096,
    ) -> Any:

        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                max_tokens=max_tokens,
                stream=False,
            )

            return response.choices[0]

        except Exception as exc:
            raise RuntimeError(
                f"Failed to communicate with vLLM "
                f"using model '{self.model}'."
            ) from exc

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[Any, None]:

        try:
            stream = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                yield chunk

        except Exception as exc:
            raise RuntimeError(
                f"Failed to communicate with vLLM "
                f"using model '{self.model}'."
            ) from exc
