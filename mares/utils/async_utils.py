"""Async helpers — concurrency-limited gather, run-in-thread, etc."""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


async def gather_with_concurrency(n: int, *coros: Awaitable[T]) -> list[T]:
    """Like :func:`asyncio.gather` but caps concurrent coroutines to ``n``."""
    if n < 1:
        raise ValueError("n must be >= 1")
    sem = asyncio.Semaphore(n)

    async def _wrap(c: Awaitable[T]) -> T:
        async with sem:
            return await c

    return await asyncio.gather(*(_wrap(c) for c in coros))


async def run_in_thread(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Run a blocking function in the default thread pool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


__all__ = ["gather_with_concurrency", "run_in_thread"]
