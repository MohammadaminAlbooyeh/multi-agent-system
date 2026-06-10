"""Research workflow — deep dive on a topic with no code generation."""

from __future__ import annotations

import asyncio

from mares.orchestrator.orchestrator import Orchestrator


TASK = (
    "Research the state of vector databases in 2026. Compare Pinecone, "
    "Weaviate, Qdrant, and pgvector. Recommend one for a startup with "
    "10M vectors and a small engineering team."
)


async def main() -> None:
    orch = Orchestrator()
    report = await orch.run(TASK)
    print(report.markdown)


if __name__ == "__main__":
    asyncio.run(main())
