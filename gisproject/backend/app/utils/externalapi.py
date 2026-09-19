from typing import Any

import httpx

DEFAULT_TIMEOUT = 30.0


async def _request(
    method: str,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    json: Any = None,
    data: Any = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.request(
            method,
            url,
            params=params,
            headers=headers,
            json=json,
            data=data,
        )
        response.raise_for_status()
        if "application/json" in response.headers.get("content-type", ""):
            return response.json()
        return response.text


async def get_api(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    return await _request("GET", url, params=params, headers=headers, timeout=timeout)


async def post_api(
    url: str,
    *,
    json: Any = None,
    data: Any = None,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    return await _request(
        "POST",
        url,
        params=params,
        headers=headers,
        json=json,
        data=data,
        timeout=timeout,
    )
