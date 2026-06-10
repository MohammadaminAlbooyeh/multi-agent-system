"""Tool registry — central catalogue of tools available to agents."""

from __future__ import annotations

from typing import Any, Callable

from mares.utils.exceptions import ToolError
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """In-memory registry mapping tool names to callables.

    Tools are async-callable objects that take a kwargs dict and return a
    JSON-serialisable result.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        func: Callable[..., Any],
        description: str = "",
        schema: dict[str, Any] | None = None,
    ) -> None:
        if name in self._tools:
            raise ToolError(f"Tool '{name}' is already registered.")
        self._tools[name] = func
        self._metadata[name] = {"description": description, "schema": schema or {}}
        logger.debug("tool.registered", name=name)

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)
        self._metadata.pop(name, None)

    def get(self, name: str) -> Callable[..., Any]:
        if name not in self._tools:
            raise ToolError(f"Tool '{name}' is not registered.")
        return self._tools[name]

    def metadata(self, name: str) -> dict[str, Any]:
        return self._metadata.get(name, {})

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def describe(self) -> list[dict[str, Any]]:
        return [
            {"name": name, **self._metadata[name]} for name in self.list_tools()
        ]


# A process-wide default registry. Tools auto-register themselves on import.
default_registry = ToolRegistry()


__all__ = ["ToolRegistry", "default_registry"]
