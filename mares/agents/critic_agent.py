"""Critic Agent — validates outputs and triggers self-correction when needed."""

from __future__ import annotations

from typing import Any, ClassVar

from mares.agents.base_agent import BaseAgent
from mares.models.agent_output import AgentOutput
from mares.models.critic_report import CriticReport
from mares.utils.exceptions import CriticError
from mares.utils.json_utils import safe_json_loads
from mares.utils.logger import get_logger

logger = get_logger(__name__)


CRITIC_SYSTEM_PROMPT = """You are the MARES Critic Agent.
Review each agent output for:
- Hallucinations (claims not supported by sources or other outputs)
- Internal consistency
- Logical / factual errors
- Completeness relative to the sub-task

Return JSON:
{
  "passed": true|false,
  "issues": [
    {"sub_task_id": 1, "severity": "low|medium|high", "description": "..."}
  ],
  "summary": "short summary"
}

Return ONLY JSON.
"""


class CriticAgent(BaseAgent):
    """Reviews a batch of :class:`AgentOutput` instances and emits a report."""

    name: ClassVar[str] = "critic_agent"
    description: ClassVar[str] = (
        "Validates all agent outputs and flags hallucinations / errors."
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(system_prompt=CRITIC_SYSTEM_PROMPT, **kwargs)

    async def run(self, input_data: list[AgentOutput]) -> CriticReport:
        if not isinstance(input_data, list):
            raise CriticError("CriticAgent expects a list of AgentOutput objects.")

        if not input_data:
            return CriticReport(passed=True, issues=[], summary="No outputs to review.")

        user_msg = "\n\n".join(out.model_dump_json() for out in input_data)
        self.remember("user", user_msg)
        logger.info("critic.start", outputs=len(input_data))

        raw = await self._generate(
            system=self.system_prompt,
            user=user_msg,
        )
        self.remember("assistant", raw)

        try:
            payload = safe_json_loads(raw)
            report = CriticReport(
                passed=bool(payload.get("passed", False)),
                issues=list(payload.get("issues", [])),
                summary=str(payload.get("summary", "")),
            )
        except (ValueError, TypeError) as exc:
            raise CriticError(f"Critic produced invalid JSON: {exc}") from exc

        self.validate_output(report)
        logger.info("critic.done", passed=report.passed, issues=len(report.issues))
        return report


__all__ = ["CriticAgent", "CRITIC_SYSTEM_PROMPT"]
