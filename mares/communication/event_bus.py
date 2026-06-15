"""Event bus — simple synchronous + async publish/subscribe for system events."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from mares.utils.logger import get_logger

logger = get_logger(__name__)


EventHandler = Callable[[dict[str, Any]], Awaitable[None] | None]


class EventBus:
    """Lightweight event bus used to wire orchestrator + UI + metrics.

    Handlers may be sync or async; both are awaited internally.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}
        self._lock = asyncio.Lock()

    def on(self, event: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def off(self, event: str, handler: EventHandler) -> None:
        if event in self._handlers:
            self._handlers[event] = [h for h in self._handlers[event] if h is not handler]

    async def emit(self, event: str, **payload: Any) -> None:
        logger.debug("event_bus.emit", event_type=event, keys=list(payload.keys()))
        handlers = list(self._handlers.get(event, []))
        results = [h(payload) for h in handlers]
        for r in results:
            if asyncio.iscoroutine(r):
                await r

    async def listeners(self, event: str) -> int:
        return len(self._handlers.get(event, []))


__all__ = ["EventBus", "EventHandler"]
