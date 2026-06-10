"""Tool Executor — invokes registered tools safely, with timeouts and retries."""

from __future__ import annotations

import asyncio
import inspect
from typing import Any

from mares.tools.tool_registry import ToolRegistry, default_registry
from mares.utils.exceptions import ToolError
from mares.utils.logger import get_logger
from mares.utils.retry import async_retry
from mares.utils.timeout import async_timeout

logger = get_logger(__name__)


class ToolExecutor:
    """Executes tools stored in a :class:`ToolRegistry`."""

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        default_timeout: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        self.registry = registry or default_registry
        self.default_timeout = default_timeout
        self.max_retries = max_retries

    async def execute(
        self,
        name: str,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Any:
        """Run a tool by name with timeout + retry."""
        tool = self.registry.get(name)
        to = timeout or self.default_timeout

        @async_retry(max_attempts=self.max_retries, exceptions=(ToolError,))
        async def _call() -> Any:
            try:
                result = await async_timeout(tool(**kwargs), seconds=to)
            except asyncio.TimeoutError as exc:
                raise ToolError(f"Tool '{name}' timed out after {to}s") from exc
            except Exception as exc:  # noqa: BLE001
                raise ToolError(f"Tool '{name}' failed: {exc}") from exc
            return result

        return await _call()

    def describe(self) -> list[dict[str, Any]]:
        return self.registry.describe()

    async def __call__(self, name: str, **kwargs: Any) -> Any:
        return await self.execute(name, **kwargs)


__all__ = ["ToolExecutor"]
