"""Unit tests for the Planner Agent."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from mares.agents.planner_agent import PlannerAgent
from mares.utils.exceptions import PlanningError


@pytest.fixture
def mock_llm_factory():
    factory = MagicMock()
    factory.generate = AsyncMock()
    return factory


@pytest.mark.asyncio
async def test_planner_parses_valid_json(mock_llm_factory):
    payload = {
        "tasks": [
            {"id": 1, "task": "First", "depends_on": []},
            {"id": 2, "task": "Second", "depends_on": [1]},
        ]
    }
    mock_llm_factory.generate.return_value = json.dumps(payload)
    agent = PlannerAgent(llm_factory=mock_llm_factory)

    plan = await agent.run("Investigate something")

    assert plan.description == "Investigate something"
    assert len(plan.sub_tasks) == 2
    assert plan.sub_tasks[1].depends_on == [1]


@pytest.mark.asyncio
async def test_planner_strips_markdown_fences(mock_llm_factory):
    payload = {"tasks": [{"id": 1, "task": "T1", "depends_on": []}]}
    mock_llm_factory.generate.return_value = f"```json\n{json.dumps(payload)}\n```"
    agent = PlannerAgent(llm_factory=mock_llm_factory)

    plan = await agent.run("test")
    assert len(plan.sub_tasks) == 1


@pytest.mark.asyncio
async def test_planner_raises_on_invalid_json(mock_llm_factory):
    mock_llm_factory.generate.return_value = "not json at all"
    agent = PlannerAgent(llm_factory=mock_llm_factory)
    with pytest.raises(PlanningError):
        await agent.run("test")


@pytest.mark.asyncio
async def test_planner_rejects_empty_input(mock_llm_factory):
    agent = PlannerAgent(llm_factory=mock_llm_factory)
    with pytest.raises(PlanningError):
        await agent.run("   ")
