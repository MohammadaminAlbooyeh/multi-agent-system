"""Parallel Runner — runs independent sub-tasks concurrently with asyncio."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from mares.models.agent_output import AgentOutput
from mares.models.sub_task import SubTask
from mares.orchestrator.scheduler import Scheduler
from mares.utils.async_utils import gather_with_concurrency
from mares.utils.logger import get_logger

logger = get_logger(__name__)


DispatchFn = Callable[[SubTask], Awaitable[AgentOutput]]


class ParallelRunner:
    """Runs a wave of independent sub-tasks in parallel.

    Uses :func:`asyncio.gather` with a concurrency cap so a large DAG does
    not overwhelm the upstream LLM API.

    Internally uses a :class:`Scheduler` for rate-limiting and metrics
    tracking (``in_flight``, ``max_seen``).
    """

    def __init__(self, max_concurrency: int = 5) -> None:
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be >= 1")
        self.max_concurrency = max_concurrency
        self._scheduler = Scheduler(max_concurrent=max_concurrency)

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler

    async def run_wave(
        self,
        sub_tasks: list[SubTask],
        dispatch: DispatchFn,
    ) -> list[AgentOutput]:
        if not sub_tasks:
            return []

        coros: list[Awaitable[AgentOutput]] = [dispatch(st) for st in sub_tasks]
        results = await gather_with_concurrency(self.max_concurrency, *coros)
        logger.debug("parallel_runner.wave", count=len(results), max_seen=self._scheduler.max_seen)
        return list(results)

    async def run_many(
        self,
        items: list[Any],
        func: Callable[[Any], Awaitable[Any]],
    ) -> list[Any]:
        """Run ``func(item)`` for every item, capped at ``max_concurrency``."""
        if not items:
            return []
        coros = [func(item) for item in items]
        return await gather_with_concurrency(self.max_concurrency, *coros)


__all__ = ["ParallelRunner", "DispatchFn"]
