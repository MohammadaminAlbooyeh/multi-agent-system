"""Tool failure simulator — inject random failures for testing resilience."""

from __future__ import annotations

import asyncio
import os
import random
from functools import wraps
from typing import Any, Callable

from mares.utils.exceptions import ToolError
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class ToolFailureSimulator:
    """Wraps a tool and randomly raises :class:`ToolError`.

    The failure rate is read from the ``TOOL_FAILURE_RATE`` env var
    (0.0 - 1.0). Use it to stress-test the self-correction loop.
    """

    def __init__(self, failure_rate: float | None = None) -> None:
        if failure_rate is None:
            failure_rate = float(os.getenv("TOOL_FAILURE_RATE", "0.0"))
        self.failure_rate = max(0.0, min(1.0, failure_rate))

    def wrap(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def inner(*args: Any, **kwargs: Any) -> Any:
            if random.random() < self.failure_rate:
                # Tiny delay so a retry decorator can recover.
                await asyncio.sleep(0.01)
                logger.warning("tool_failure_simulator.injected", fn=func.__name__)
                raise ToolError(
                    f"Simulated failure in {func.__name__} "
                    f"(rate={self.failure_rate:.2f})"
                )
            return await func(*args, **kwargs)

        return inner


__all__ = ["ToolFailureSimulator"]
