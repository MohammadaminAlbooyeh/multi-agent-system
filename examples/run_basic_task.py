"""Basic MARES example — run a single planning + research task.

Run with:

    python -m examples.run_basic_task
"""

from __future__ import annotations

import asyncio

from mares.orchestrator.orchestrator import Orchestrator


TASK = (
    "Explain the differences between asyncio task groups and "
    "thread pools in Python, and recommend a default for I/O-bound work."
)


async def main() -> None:
    orch = Orchestrator()
    report = await orch.run(TASK)
    print(report.markdown)


if __name__ == "__main__":
    asyncio.run(main())
