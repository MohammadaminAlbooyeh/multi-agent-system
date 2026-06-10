"""Unit tests for the Critic Agent."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from mares.agents.critic_agent import CriticAgent
from mares.models.agent_output import AgentOutput


@pytest.fixture
def mock_llm_factory():
    factory = MagicMock()
    factory.generate = AsyncMock()
    return factory


@pytest.mark.asyncio
async def test_critic_passes_on_clean_output(mock_llm_factory):
    mock_llm_factory.generate.return_value = json.dumps(
        {"passed": True, "issues": [], "summary": "all good"}
    )
    agent = CriticAgent(llm_factory=mock_llm_factory)

    outputs = [
        AgentOutput(agent="research_agent", sub_task_id=1, content={"summary": "ok"}),
    ]
    report = await agent.run(outputs)
    assert report.passed is True
    assert report.issues == []


@pytest.mark.asyncio
async def test_critic_flags_issues(mock_llm_factory):
    mock_llm_factory.generate.return_value = json.dumps(
        {
            "passed": False,
            "issues": [{"sub_task_id": 1, "severity": "high", "description": "fact wrong"}],
            "summary": "issues found",
        }
    )
    agent = CriticAgent(llm_factory=mock_llm_factory)
    report = await agent.run(
        [AgentOutput(agent="research_agent", sub_task_id=1, content={})]
    )
    assert report.passed is False
    assert report.failed_subtask_ids() == {1}


@pytest.mark.asyncio
async def test_critic_handles_empty_input(mock_llm_factory):
    agent = CriticAgent(llm_factory=mock_llm_factory)
    report = await agent.run([])
    assert report.passed is True
    mock_llm_factory.generate.assert_not_called()
