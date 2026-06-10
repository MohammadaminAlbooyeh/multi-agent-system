"""Top-level Orchestrator: ties agents, DAG, and self-correction together."""

from __future__ import annotations

from typing import Any

from mares.agents.critic_agent import CriticAgent
from mares.agents.execution_agent import ExecutionAgent
from mares.agents.planner_agent import PlannerAgent
from mares.agents.research_agent import ResearchAgent
from mares.agents.synthesizer_agent import SynthesizerAgent
from mares.models.agent_output import AgentOutput
from mares.models.final_report import FinalReport
from mares.models.task import Task
from mares.orchestrator.dag_executor import DAGExecutor
from mares.orchestrator.self_correction_loop import SelfCorrectionLoop
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    """The main entry point for running a MARES task end-to-end.

    Responsibilities:
        1. Call the Planner → produce a :class:`Task` (DAG).
        2. Execute the DAG → collect :class:`AgentOutput` instances.
        3. Run the Critic and (optionally) re-run on failure.
        4. Run the Synthesizer → return a :class:`FinalReport`.
    """

    def __init__(
        self,
        planner: PlannerAgent | None = None,
        research: ResearchAgent | None = None,
        execution: ExecutionAgent | None = None,
        critic: CriticAgent | None = None,
        synthesizer: SynthesizerAgent | None = None,
        self_correction: SelfCorrectionLoop | None = None,
        dag_executor: DAGExecutor | None = None,
        max_retries: int = 3,
    ) -> None:
        self.planner = planner or PlannerAgent()
        self.research = research or ResearchAgent()
        self.execution = execution or ExecutionAgent()
        self.critic = critic or CriticAgent()
        self.synthesizer = synthesizer or SynthesizerAgent()
        self.dag_executor = dag_executor or DAGExecutor(self.research, self.execution)
        self.self_correction = self_correction or SelfCorrectionLoop(
            self.dag_executor,
            self.critic,
            max_retries=max_retries,
        )

    async def run(self, user_task: str) -> FinalReport:
        """Execute the full pipeline and return a :class:`FinalReport`."""
        logger.info("orchestrator.start", task=user_task[:80])

        # 1) Plan
        plan: Task = await self.planner.run(user_task)

        # 2) Execute DAG (with self-correction on critic failure)
        outputs: list[AgentOutput] = await self.self_correction.run(plan)

        # 3) Synthesize
        report = await self.synthesizer.run(outputs)
        logger.info("orchestrator.done")
        return report

    async def plan_only(self, user_task: str) -> Task:
        return await self.planner.run(user_task)

    async def execute_plan(self, plan: Task) -> list[AgentOutput]:
        return await self.dag_executor.run(plan)


__all__ = ["Orchestrator"]
