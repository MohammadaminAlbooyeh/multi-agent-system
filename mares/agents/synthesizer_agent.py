"""Synthesizer Agent — combines all validated outputs into a final Markdown report."""

from __future__ import annotations

from typing import Any, ClassVar

from mares.agents.base_agent import BaseAgent
from mares.models.agent_output import AgentOutput
from mares.models.final_report import FinalReport
from mares.utils.logger import get_logger

logger = get_logger(__name__)


SYNTHESIZER_SYSTEM_PROMPT = """You are the MARES Synthesizer Agent.
You receive ALL agent outputs (research findings, execution results, critic
review) and produce a clean final Markdown report.

Structure:
# MARES Final Report
## Problem Decomposition
## Research Findings
## Code Prototype (if any)
## Critic Review
## Final Recommendation

Write clearly. Cite sources. No JSON. Return ONLY the Markdown body.
"""


class SynthesizerAgent(BaseAgent):
    """Builds the user-facing final report from all upstream outputs."""

    name: ClassVar[str] = "synthesizer_agent"
    description: ClassVar[str] = "Combines outputs into a final Markdown report."

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(system_prompt=SYNTHESIZER_SYSTEM_PROMPT, **kwargs)

    async def run(self, input_data: list[AgentOutput]) -> FinalReport:
        if not isinstance(input_data, list):
            raise TypeError("SynthesizerAgent expects a list of AgentOutput objects.")

        # Defensive: in some pipelines a critic report may be passed in a
        # "critic" key, separated from the agent outputs.
        user_msg = "\n\n---\n\n".join(out.model_dump_json() for out in input_data)
        self.remember("user", user_msg)
        logger.info("synthesizer.start", outputs=len(input_data))

        body = await self.llm_factory.generate(
            system=self.system_prompt,
            user=user_msg,
        )
        self.remember("assistant", body)

        report = FinalReport(
            markdown=body,
            sources=[
                src
                for out in input_data
                for src in (out.metadata or {}).get("sources", [])
            ],
        )
        self.validate_output(report)
        logger.info("synthesizer.done", length=len(body))
        return report


__all__ = ["SynthesizerAgent", "SYNTHESIZER_SYSTEM_PROMPT"]
