"""Data pipeline example — multi-step ETL with code execution."""

from __future__ import annotations

import asyncio

from mares.orchestrator.orchestrator import Orchestrator


TASK = (
    "Design an end-to-end data pipeline that ingests CSV files from S3, "
    "cleans missing values, computes daily aggregates, and stores the "
    "result in PostgreSQL. Provide working code."
)


async def main() -> None:
    orch = Orchestrator()
    report = await orch.run(TASK)
    print(report.markdown)


if __name__ == "__main__":
    asyncio.run(main())
