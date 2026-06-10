# Async Guide

MARES is built on `asyncio` from the ground up. Every agent's `run`
method is `async def`. Independent sub-tasks run concurrently inside
`gather_with_concurrency`, which wraps `asyncio.gather` with a semaphore
so the LLM provider is never overwhelmed.

## Key primitives

| Primitive | Where | Purpose |
|-----------|-------|---------|
| `gather_with_concurrency` | `utils/async_utils.py` | Bounded `gather`. |
| `ParallelRunner.run_wave` | `orchestrator/parallel_runner.py` | Run all sub-tasks in a wave. |
| `Scheduler` | `orchestrator/scheduler.py` | Per-task backpressure. |
| `async_timeout` | `utils/timeout.py` | Hard timeout for any coroutine. |
| `async_retry` | `utils/retry.py` | Exponential backoff with jitter. |

## Pattern: run N independent calls

```python
from mares.utils.async_utils import gather_with_concurrency

async def call(i: int) -> int:
    return i * 2

results = await gather_with_concurrency(5, *(call(i) for i in range(20)))
```
