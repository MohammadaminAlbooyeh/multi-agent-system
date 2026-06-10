"""Search tool — web search (real SerpAPI or mock results)."""

from __future__ import annotations

import os
from typing import Any

from mares.tools.tool_registry import default_registry
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class SearchTool:
    """Async web search tool.

    Set the ``SERPAPI_API_KEY`` environment variable to enable real search.
    Without it, the tool returns deterministic mock results — useful for
    development and unit tests.
    """

    name = "search"
    description = "Search the web for a query. Returns a list of results."

    async def __call__(self, query: str, num_results: int = 5, **_: Any) -> list[dict[str, Any]]:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return self._mock_results(query, num_results)
        return await self._real_search(query, num_results, api_key)

    def _mock_results(self, query: str, n: int) -> list[dict[str, Any]]:
        return [
            {
                "title": f"Mock result {i + 1} for '{query}'",
                "url": f"https://example.com/mock-{i + 1}",
                "snippet": f"This is a mocked search result number {i + 1} for the query '{query}'.",
            }
            for i in range(n)
        ]

    async def _real_search(self, query: str, n: int, api_key: str) -> list[dict[str, Any]]:
        # Lazy import to avoid a hard dep when the key is missing.
        try:
            from serpapi import GoogleSearch  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "google-search-results not installed; pip install google-search-results"
            ) from exc

        params = {"q": query, "num": n, "api_key": api_key}
        logger.info("search.real", query=query)
        search = GoogleSearch(params)
        data = search.get_dict()
        organic = data.get("organic_results", [])[:n]
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "snippet": r.get("snippet", ""),
            }
            for r in organic
        ]


# Auto-register on import.
default_registry.register(
    SearchTool.name,
    SearchTool().__call__,
    description=SearchTool.description,
    schema={"query": "string", "num_results": "integer"},
)


__all__ = ["SearchTool"]
