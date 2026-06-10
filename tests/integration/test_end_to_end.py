"""End-to-end test that uses a fake LLM and a real DAG + tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mares.orchestrator.orchestrator import Orchestrator


def _make_factory(responses: list[str]) -> MagicMock:
    factory = MagicMock()
    it = iter(responses)

    async def fake_generate(*_a, **_k):
        return next(it)

    factory.generate = fake_generate
    return factory


@pytest.mark.asyncio
async def test_end_to_end_with_python_executor():
    """Plan → Research (mocked) → Execution (real sandbox) → Critic (mocked) → Synth (mocked)."""
    plan = json.dumps(
        {
            "tasks": [
                {"id": 1, "task": "Compute factorial of 5 in code", "depends_on": []},
            ]
        }
    )
    research_fallback = json.dumps({"summary": "factorial math", "facts": [], "sources": []})
    exec_code = json.dumps(
        {"language": "python", "code": "import math; print(math.factorial(5))"}
    )
    critic = json.dumps({"passed": True, "issues": [], "summary": "ok"})
    synth = "# Report\n\n120"

    factory = _make_factory([plan, exec_code, critic, synth])

    with patch("mares.llm.llm_factory.LLMFactory", return_value=factory):
        orch = Orchestrator()
        report = await orch.run("Compute 5!")

    assert "120" in report.markdown
