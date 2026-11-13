"""Search tool — real web search with pluggable providers and a keyless fallback.

Supported providers (selected via ``SEARCH_PROVIDER``):

* ``serpapi``    — Google results via SerpAPI (requires ``SERPAPI_API_KEY``)
* ``brave``      — Brave Search API (requires ``BRAVE_API_KEY``)
* ``duckduckgo`` — DuckDuckGo HTML endpoint (no key required)
* ``mock``       — deterministic fixtures, for tests only

``auto`` (the default) picks SerpAPI when a key is configured, then Brave,
then DuckDuckGo. There is no silent mock fallback: a misconfigured or
unreachable provider raises :class:`ToolError` so callers can retry or
degrade explicitly.
"""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

from mares.tools.tool_registry import default_registry
from mares.utils.exceptions import ToolError
from mares.utils.logger import get_logger

logger = get_logger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)
_DEFAULT_TIMEOUT = 30.0


class SearchTool:
    """Async web search tool returning ``title``/``url``/``snippet`` records."""

    name = "search"
    description = "Search the web for a query. Returns a list of results."

    def __init__(
        self,
        provider: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.provider = (
            provider or os.getenv("SEARCH_PROVIDER") or "auto"
        ).strip().lower()
        timeout_str = os.getenv("SEARCH_TIMEOUT_SECONDS")
        self.timeout = timeout or (float(timeout_str) if timeout_str else _DEFAULT_TIMEOUT)

    async def __call__(
        self, query: str, num_results: int = 5, **_: Any
    ) -> list[dict[str, Any]]:
        query = (query or "").strip()
        if not query:
            raise ToolError("search requires a non-empty `query`.")
        num_results = max(1, min(int(num_results), 20))

        provider = self._resolve_provider()
        logger.info("search.start", provider=provider, query=query, num_results=num_results)

        if provider == "mock":
            return self._mock_results(query, num_results)
        if provider == "serpapi":
            results = await self._serpapi_search(query, num_results)
        elif provider == "brave":
            results = await self._brave_search(query, num_results)
        elif provider == "duckduckgo":
            results = await self._duckduckgo_search(query, num_results)
        else:  # pragma: no cover - guarded by _resolve_provider
            raise ToolError(f"Unsupported search provider: {provider}")

        results = results[:num_results]
        if not results:
            logger.warning("search.empty", provider=provider, query=query)
        return results

    # ----- Provider selection -------------------------------------------------

    def _resolve_provider(self) -> str:
        if self.provider not in {"auto", "serpapi", "brave", "duckduckgo", "mock"}:
            raise ToolError(
                f"Unsupported SEARCH_PROVIDER '{self.provider}'. "
                "Choose auto|serpapi|brave|duckduckgo|mock."
            )
        if self.provider != "auto":
            return self.provider
        if os.getenv("SERPAPI_API_KEY"):
            return "serpapi"
        if os.getenv("BRAVE_API_KEY"):
            return "brave"
        return "duckduckgo"

    # ----- Providers ----------------------------------------------------------

    async def _serpapi_search(self, query: str, n: int) -> list[dict[str, Any]]:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            raise ToolError("SERPAPI_API_KEY is not set.")
        params: dict[str, str | int] = {
            "engine": "google",
            "q": query,
            "num": n,
            "api_key": api_key,
        }
        async with self._client() as client:
            response = await client.get("https://serpapi.com/search.json", params=params)
            self._raise_for_status(response, "SerpAPI")
            data = response.json()
        return [
            {
                "title": str(r.get("title", "")),
                "url": str(r.get("link", "")),
                "snippet": str(r.get("snippet", "")),
            }
            for r in data.get("organic_results", [])[:n]
        ]

    async def _brave_search(self, query: str, n: int) -> list[dict[str, Any]]:
        api_key = os.getenv("BRAVE_API_KEY")
        if not api_key:
            raise ToolError("BRAVE_API_KEY is not set.")
        headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
        params: dict[str, str | int] = {"q": query, "count": n}
        async with self._client() as client:
            response = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params=params,
                headers=headers,
            )
            self._raise_for_status(response, "Brave Search")
            data = response.json()
        return [
            {
                "title": str(r.get("title", "")),
                "url": str(r.get("url", "")),
                "snippet": str(r.get("description", "")),
            }
            for r in data.get("web", {}).get("results", [])[:n]
        ]

    async def _duckduckgo_search(self, query: str, n: int) -> list[dict[str, Any]]:
        headers = {
            "User-Agent": _USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://duckduckgo.com/",
        }
        async with self._client() as client:
            response = await client.post(
                "https://html.duckduckgo.com/html/",
                data={"q": query, "kl": "us-en"},
                headers=headers,
            )
            self._raise_for_status(response, "DuckDuckGo")
        return self._parse_duckduckgo_html(response.text, n)

    # ----- Parsing helpers ----------------------------------------------------

    @staticmethod
    def _parse_duckduckgo_html(html: str, n: int) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        results: list[dict[str, Any]] = []
        for block in soup.select("div.result"):
            link = block.select_one("a.result__a")
            if link is None:
                continue
            title = link.get_text(" ", strip=True)
            url = SearchTool._unwrap_duckduckgo_url(str(link.get("href", "")))
            if not title or not url:
                continue
            snippet_el = block.select_one(".result__snippet")
            snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
            results.append({"title": title, "url": url, "snippet": snippet})
            if len(results) >= n:
                break
        return results

    @staticmethod
    def _unwrap_duckduckgo_url(url: str) -> str:
        """Unwrap ``/l/?uddg=...`` redirects into the real destination."""
        if not url:
            return ""
        if url.startswith("//"):
            url = "https:" + url
        parsed = urlparse(url)
        if parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
            target = parse_qs(parsed.query).get("uddg", [""])[0]
            return unquote(target)
        return url

    @staticmethod
    def _mock_results(query: str, n: int) -> list[dict[str, Any]]:
        return [
            {
                "title": f"Mock result {i + 1} for '{query}'",
                "url": f"https://example.com/mock-{i + 1}",
                "snippet": (
                    f"This is a mocked search result number {i + 1} "
                    f"for the query '{query}'."
                ),
            }
            for i in range(n)
        ]

    # ----- Shared HTTP helpers ------------------------------------------------

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={"User-Agent": _USER_AGENT},
        )

    @staticmethod
    def _raise_for_status(response: httpx.Response, provider: str) -> None:
        if response.status_code >= 400:
            raise ToolError(
                f"{provider} search failed with HTTP {response.status_code}."
            )


# Auto-register on import.
default_registry.register(
    SearchTool.name,
    SearchTool().__call__,
    description=SearchTool.description,
    schema={"query": "string", "num_results": "integer"},
)


__all__ = ["SearchTool"]
