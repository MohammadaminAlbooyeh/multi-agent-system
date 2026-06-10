"""Unit tests for the Research Agent."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from mares.agents.research_agent import ResearchAgent
from mares.models.sub_task import SubTask
from mares.utils.exceptions import ResearchError


@pytest.fixture
def mock_llm_factory():
    factory = MagicMock()
    factory.generate = AsyncMock()
    return factory


@pytest.mark.asyncio
async def test_research_produces_finding(mock_llm_factory):
    payload = {
        "summary": "Celery uses a broker to dispatch tasks.",
        "facts": ["Celery is written in Python", "It supports Redis and RabbitMQ"],
        "sources": ["https://docs.celeryq.dev"],
    }
    mock_llm_factory.generate.return_value = json.dumps(payload)
    agent = ResearchAgent(llm_factory=mock_llm_factory)

    finding = await agent.run(SubTask(id=1, task="What is Celery?"))
    assert finding.sub_task_id == 1
    assert "Celery" in finding.summary
    assert len(finding.facts) == 2
    assert "https://docs.celeryq.dev" in finding.sources


@pytest.mark.asyncio
async def test_research_rejects_wrong_input_type(mock_llm_factory):
    agent = ResearchAgent(llm_factory=mock_llm_factory)
    with pytest.raises(ResearchError):
        await agent.run("not a sub-task")  # type: ignore[arg-type]
