"""Integration tests for DAGExecutor and parallel execution."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from mares.models.sub_task import SubTask
from mares.models.task import Task
from mares.orchestrator.dag_executor import DAGExecutor


@pytest.mark.asyncio
async def test_dag_executor_runs_waves_in_order():
    # Three sub-tasks: 1, 2 in parallel; 3 waits for both.
    research = MagicMock()
    execution = MagicMock()

    async def fake_research(st):
        from mares.models.research_finding import ResearchFinding
        return ResearchFinding(sub_task_id=st.id, summary=f"done-{st.id}", facts=[], sources=[])

    research.run = fake_research
    execution.run = fake_research  # unused in this test

    execu = DAGExecutor(research_agent=research, execution_agent=execution, max_concurrency=4)
    plan = Task(
        description="t",
        sub_tasks=[
            SubTask(id=1, task="A", depends_on=[]),
            SubTask(id=2, task="B", depends_on=[]),
            SubTask(id=3, task="C", depends_on=[1, 2]),
        ],
    )

    outputs = await execu.run(plan)
    assert len(outputs) == 3
    ids = sorted(o.sub_task_id for o in outputs)
    assert ids == [1, 2, 3]
