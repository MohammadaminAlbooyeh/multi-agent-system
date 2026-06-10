"""Unit tests for the Execution Agent."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from mares.agents.execution_agent import ExecutionAgent
from mares.models.sub_task import SubTask
from mares.tools.python_executor_tool import PythonExecutorTool


@pytest.fixture
def mock_llm_factory():
    factory = MagicMock()
    factory.generate = AsyncMock()
    return factory


@pytest.mark.asyncio
async def test_execution_runs_python(mock_llm_factory):
    payload = {"language": "python", "code": "print('hi')"}
    mock_llm_factory.generate.return_value = json.dumps(payload)
    executor = PythonExecutorTool(default_timeout=5)
    agent = ExecutionAgent(llm_factory=mock_llm_factory, executor=executor)

    result = await agent.run(SubTask(id=1, task="print hello"))
    assert result.success is True
    assert "hi" in result.stdout
    assert result.language == "python"


@pytest.mark.asyncio
async def test_execution_captures_runtime_errors(mock_llm_factory):
    payload = {"language": "python", "code": "raise ValueError('boom')"}
    mock_llm_factory.generate.return_value = json.dumps(payload)
    executor = PythonExecutorTool(default_timeout=5)
    agent = ExecutionAgent(llm_factory=mock_llm_factory, executor=executor)

    result = await agent.run(SubTask(id=1, task="raise"))
    assert result.success is False
    assert "ValueError" in result.stderr or "boom" in result.stderr
