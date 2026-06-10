"""Algorithm task — implement and test a classic CS algorithm."""

from __future__ import annotations

import asyncio

from mares.orchestrator.orchestrator import Orchestrator


TASK = (
    "Implement a balanced binary search tree (AVL tree) in Python with "
    "insert, delete, and search operations. Include a quick test that "
    "verifies correctness."
)


async def main() -> None:
    orch = Orchestrator()
    report = await orch.run(TASK)
    print(report.markdown)


if __name__ == "__main__":
    asyncio.run(main())
