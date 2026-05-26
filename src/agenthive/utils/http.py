"""HTTP utility functions for agent communication."""

from __future__ import annotations

from typing import Any

import httpx


async def send_request(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> httpx.Response:
    """Send an HTTP request to an agent endpoint.

    Args:
        url: Target URL.
        method: HTTP method.
        headers: Optional headers.
        json_body: Optional JSON body.
        timeout: Request timeout in seconds.

    Returns:
        The HTTP response.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.request(
            method=method,
            url=url,
            headers=headers or {},
            json=json_body,
        )


async def check_url_reachable(url: str, timeout: float = 5.0) -> bool:
    """Check if a URL is reachable.

    Args:
        url: URL to check.
        timeout: Timeout in seconds.

    Returns:
        True if the URL is reachable.
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            return response.status_code < 500
    except (httpx.HTTPError, OSError):
        return False
