"""HTTP API call tool — perform authenticated GET/POST calls to external APIs."""

from __future__ import annotations

from typing import Any

import httpx

from mares.tools.tool_registry import default_registry
from mares.utils.exceptions import ToolError
from mares.utils.logger import get_logger
from mares.utils.retry import async_retry

logger = get_logger(__name__)


class APICallTool:
    """Thin async wrapper around :mod:`httpx` with auth, timeout, retry."""

    name = "api_call"
    description = "Make an HTTP GET/POST request to an external API."

    def __init__(
        self,
        default_timeout: float = 15.0,
        max_retries: int = 3,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.default_headers = default_headers or {}

    @async_retry(max_attempts=3, exceptions=(httpx.HTTPError,))
    async def __call__(
        self,
        method: str = "GET",
        url: str = "",
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **_: Any,
    ) -> dict[str, Any]:
        if not url:
            raise ToolError("api_call requires a non-empty `url`.")
        method = method.upper()
        if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            raise ToolError(f"Unsupported HTTP method: {method}")

        merged_headers = {**self.default_headers, **(headers or {})}
        to = timeout or self.default_timeout
        logger.info("api_call.start", method=method, url=url)

        async with httpx.AsyncClient(timeout=to) as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=merged_headers,
            )
            try:
                body = response.json()
            except ValueError:
                body = response.text

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": body,
            }


# Auto-register on import.
default_registry.register(
    APICallTool.name,
    APICallTool().__call__,
    description=APICallTool.description,
    schema={"method": "GET|POST|PUT|PATCH|DELETE", "url": "string"},
)

__all__ = ["APICallTool"]
