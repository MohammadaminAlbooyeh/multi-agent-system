"""Timeout utility — async wrapper around :func:`asyncio.wait_for`."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import TypeVar

from mares.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


async def async_timeout(coro: Awaitable[T], seconds: float) -> T:
    """Await ``coro`` raising :class:`asyncio.TimeoutError` after ``seconds``."""
    logger.debug("timeout.start", seconds=seconds)
    return await asyncio.wait_for(coro, timeout=seconds)


__all__ = ["async_timeout"]
