"""Retry decorator — exponential backoff for sync and async functions."""

from __future__ import annotations

import asyncio
import functools
import random
import time
from collections.abc import Callable
from typing import Any, TypeVar

from mares.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Sync retry decorator with exponential backoff + jitter."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error("retry.exhausted", fn=func.__name__, attempts=attempt)
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay += random.random() * 0.1 * delay
                    logger.warning(
                        "retry.attempt",
                        fn=func.__name__,
                        attempt=attempt,
                        error=str(exc),
                        sleep=delay,
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


def async_retry(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Async retry decorator with exponential backoff + jitter."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error("async_retry.exhausted", fn=func.__name__, attempts=attempt)
                        raise
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay += random.random() * 0.1 * delay
                    logger.warning(
                        "async_retry.attempt",
                        fn=func.__name__,
                        attempt=attempt,
                        error=str(exc),
                        sleep=delay,
                    )
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


__all__ = ["retry", "async_retry"]
