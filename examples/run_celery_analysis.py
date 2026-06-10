"""Celery failure analysis — the canonical MARES demo.

Run with:

    python -m examples.run_celery_analysis
"""

from __future__ import annotations

import asyncio

from mares.orchestrator.orchestrator import Orchestrator


TASK = (
    "Analyze why Celery tasks fail intermittently in distributed systems "
    "and propose a scalable fix."
)


async def main() -> None:
    orch = Orchestrator()
    report = await orch.run(TASK)
    print(report.markdown)


if __name__ == "__main__":
    asyncio.run(main())
