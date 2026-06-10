"""Integration tests for the ParallelRunner."""

from __future__ import annotations

import asyncio
import time

import pytest

from mares.models.agent_output import AgentOutput
from mares.orchestrator.parallel_runner import ParallelRunner


@pytest.mark.asyncio
async def test_parallel_runner_runs_concurrently():
    runner = ParallelRunner(max_concurrency=3)

    async def dispatch(idx: int) -> AgentOutput:
        await asyncio.sleep(0.1)
        return AgentOutput(agent="test", sub_task_id=idx, content={})

    start = time.perf_counter()
    results = await runner.run_wave([1, 2, 3], dispatch)
    elapsed = time.perf_counter() - start

    assert len(results) == 3
    # 3 tasks of 100ms each, run in parallel → ~0.1s, definitely < 0.3s.
    assert elapsed < 0.25


@pytest.mark.asyncio
async def test_parallel_runner_respects_concurrency_cap():
    runner = ParallelRunner(max_concurrency=2)
    in_flight = 0
    peak = 0

    async def dispatch(idx: int) -> AgentOutput:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.05)
        in_flight -= 1
        return AgentOutput(agent="t", sub_task_id=idx, content={})

    await runner.run_wave([1, 2, 3, 4], dispatch)
    assert peak <= 2
