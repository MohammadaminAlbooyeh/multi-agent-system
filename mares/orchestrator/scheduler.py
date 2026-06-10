"""Task scheduler — assigns sub-tasks to worker slots over time.

This is a thin async scheduler used for backpressure / rate limiting when
many sub-tasks are scheduled at once. It does *not* handle dependencies —
that's the :class:`DAGExecutor`'s job. It only ensures we never have more
than ``max_concurrent`` sub-tasks in flight.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import TypeVar

from mares.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class Scheduler:
    """Async semaphore-based scheduler."""

    def __init__(self, max_concurrent: int = 5) -> None:
        if max_concurrent < 1:
            raise ValueError("max_concurrent must be >= 1")
        self._sem = asyncio.Semaphore(max_concurrent)
        self._in_flight = 0
        self._max_seen = 0

    @property
    def in_flight(self) -> int:
        return self._in_flight

    @property
    def max_seen(self) -> int:
        return self._max_seen

    async def submit(self, coro_factory: Awaitable[T]) -> T:
        async with self._sem:
            self._in_flight += 1
            self._max_seen = max(self._max_seen, self._in_flight)
            logger.debug("scheduler.submit", in_flight=self._in_flight)
            try:
                return await coro_factory
            finally:
                self._in_flight -= 1

    async def map(self, items: list, func) -> list:
        coros = [self.submit(func(item)) for item in items]
        return await asyncio.gather(*coros)


__all__ = ["Scheduler"]
