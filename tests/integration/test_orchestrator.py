"""Integration tests for the full Orchestrator pipeline."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mares.orchestrator.orchestrator import Orchestrator


def _stub_llm_factory(responses: list[str]):
    factory = MagicMock()
    iter_resp = iter(responses)

    async def fake_generate(*_args, **_kwargs):
        return next(iter_resp)

    factory.generate = fake_generate
    return factory


@pytest.mark.asyncio
async def test_orchestrator_runs_end_to_end():
    plan_payload = json.dumps(
        {
            "tasks": [
                {"id": 1, "task": "Research X", "depends_on": []},
                {"id": 2, "task": "Implement Y", "depends_on": [1]},
            ]
        }
    )
    research_payload = json.dumps(
        {"summary": "X is documented", "facts": ["f1"], "sources": ["s1"]}
    )
    exec_payload = json.dumps({"language": "python", "code": "print('ok')"})
    critic_payload = json.dumps({"passed": True, "issues": [], "summary": "ok"})
    synth_payload = "# Final\n\nAll good."

    factory = _stub_llm_factory([plan_payload, research_payload, exec_payload, critic_payload, synth_payload])

    with patch("mares.llm.llm_factory.LLMFactory", return_value=factory):
        orch = Orchestrator()
        report = await orch.run("Investigate X and implement Y")

    assert "Final" in report.markdown
