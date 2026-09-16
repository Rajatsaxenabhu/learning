from collections.abc import AsyncGenerator
from typing import Any

from ollama import AsyncClient


class LLMClient:

    def __init__(
        self,
         model: str = "qwen3:14b",
        host: str = "http://localhost:11434",
    ):
        self.model = model
        self._client = AsyncClient(host=host)

    async def chat_once(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:

        try:
            return await self._client.chat(
                model=self.model,
                messages=messages,
                tools=tools,
                stream=False,
            )

        except Exception as exc:
            raise RuntimeError(
                f"Failed to communicate with Ollama "
                f"using model '{self.model}'."
            ) from exc

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncGenerator[Any, None]:

        try:
            stream = await self._client.chat(
                model=self.model,
                messages=messages,
                tools=tools,
                stream=True,
            )

            async for chunk in stream:
                yield chunk

        except Exception as exc:
            raise RuntimeError(
                f"Failed to communicate with Ollama "
                f"using model '{self.model}'."
            ) from exc