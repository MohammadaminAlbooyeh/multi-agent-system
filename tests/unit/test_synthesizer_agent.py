"""Unit tests for the Synthesizer Agent."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from mares.agents.synthesizer_agent import SynthesizerAgent
from mares.models.agent_output import AgentOutput


@pytest.fixture
def mock_llm_factory():
    factory = MagicMock()
    factory.generate = AsyncMock(return_value="# MARES Final Report\n\nAll good.")
    return factory


@pytest.mark.asyncio
async def test_synthesizer_builds_markdown_report(mock_llm_factory):
    agent = SynthesizerAgent(llm_factory=mock_llm_factory)
    outputs = [
        AgentOutput(
            agent="research_agent",
            sub_task_id=1,
            content={"summary": "ok"},
            metadata={"sources": ["https://a.com"]},
        ),
        AgentOutput(agent="execution_agent", sub_task_id=2, content={"stdout": "x"}),
    ]
    report = await agent.run(outputs)

    assert "MARES Final Report" in report.markdown
    assert "https://a.com" in report.sources
    mock_llm_factory.generate.assert_awaited_once()
