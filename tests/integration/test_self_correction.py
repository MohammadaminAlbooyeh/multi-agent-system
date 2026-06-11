"""Integration tests for the SelfCorrectionLoop."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from mares.models.agent_output import AgentOutput
from mares.models.sub_task import SubTask
from mares.models.task import Task
from mares.orchestrator.self_correction_loop import SelfCorrectionLoop


@pytest.mark.asyncio
async def test_self_correction_reruns_failed_subtasks():
    # DAG with 2 sub-tasks, where sub-task 1 always fails the critic.
    executor = MagicMock()
    critic = MagicMock()

    call_count = {"n": 0}

    async def fake_execute(plan: Task):
        call_count["n"] += 1
        return [
            AgentOutput(agent="research_agent", sub_task_id=1, content={}),
            AgentOutput(agent="research_agent", sub_task_id=2, content={}),
        ]

    executor.run = fake_execute

    reports = [
        # First critic call: fail on sub-task 1
        MagicMock(passed=False, issues=[MagicMock(sub_task_id=1, severity="high", description="bad")]),
        # Second critic call: pass
        MagicMock(passed=True, issues=[]),
        # Third (final) call after exhausting retries
        MagicMock(passed=True, issues=[]),
    ]
    reports_iter = iter(reports)

    async def fake_critic(_outputs):
        return next(reports_iter)

    critic.run = fake_critic

    loop = SelfCorrectionLoop(dag_executor=executor, critic=critic, max_retries=2)
    plan = Task(
        description="t",
        sub_tasks=[
            SubTask(id=1, task="A", depends_on=[]),
            SubTask(id=2, task="B", depends_on=[]),
        ],
    )

    outputs = await loop.run(plan)
    assert outputs  # we have outputs
    assert call_count["n"] >= 2  # we re-ran at least once
