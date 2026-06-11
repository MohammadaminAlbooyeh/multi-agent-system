"""Top-level Orchestrator: ties agents, DAG, and self-correction together."""

from __future__ import annotations

from typing import Any

from mares.agents.critic_agent import CriticAgent
from mares.agents.execution_agent import ExecutionAgent
from mares.agents.planner_agent import PlannerAgent
from mares.agents.research_agent import ResearchAgent
from mares.agents.synthesizer_agent import SynthesizerAgent
from mares.communication.event_bus import EventBus
from mares.evaluation.consistency_checker import ConsistencyChecker
from mares.evaluation.hallucination_detector import HallucinationDetector
from mares.llm.cost_controller import CostController
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
        cost_controller: CostController | None = None,
        event_bus: EventBus | None = None,
        max_retries: int = 3,
    ) -> None:
        cost_controller = cost_controller or CostController.from_env()
        cc_kwargs = {"cost_controller": cost_controller}
        self.planner = planner or PlannerAgent(**cc_kwargs)
        self.research = research or ResearchAgent(**cc_kwargs)
        self.execution = execution or ExecutionAgent(**cc_kwargs)
        self.critic = critic or CriticAgent(**cc_kwargs)
        self.synthesizer = synthesizer or SynthesizerAgent(**cc_kwargs)
        self.cost_controller = cost_controller
        self.hallucination_detector = HallucinationDetector()
        self.consistency_checker = ConsistencyChecker()
        self.event_bus = event_bus
        self.dag_executor = dag_executor or DAGExecutor(self.research, self.execution)
        self.self_correction = self_correction or SelfCorrectionLoop(
            self.dag_executor,
            self.critic,
            max_retries=max_retries,
        )

    async def run(self, user_task: str, task_id: str | None = None) -> FinalReport:
        """Execute the full pipeline and return a :class:`FinalReport`."""
        logger.info("orchestrator.start", task=user_task[:80])

        await self._emit("task.progress", stage="plan", task_id=task_id)

        # 1) Plan
        plan: Task = await self.planner.run(user_task)

        await self._emit("task.progress", stage="execute", task_id=task_id, sub_tasks=len(plan.sub_tasks))

        # 2) Execute DAG (with self-correction on critic failure)
        outputs: list[AgentOutput] = await self.self_correction.run(plan)

        await self._emit("task.progress", stage="evaluate", task_id=task_id, outputs=len(outputs))

        # 3) Evaluate
        eval_info: dict[str, Any] = {}
        try:
            all_text = "\n".join(
                str(o.content) for o in outputs if o.content
            )
            all_sources = [
                src for o in outputs
                for src in (o.metadata or {}).get("sources", [])
            ]
            eval_info["hallucinations"] = self.hallucination_detector.detect(all_text, all_sources)
            eval_info["consistency"] = self.consistency_checker.check(outputs)
            eval_info["cost"] = self.cost_controller.snapshot() if self.cost_controller else {}
        except Exception as exc:  # noqa: BLE001
            logger.warning("orchestrator.eval_failed", error=str(exc))

        await self._emit("task.progress", stage="synthesize", task_id=task_id)

        # 4) Synthesize
        report = await self.synthesizer.run(outputs)
        report.metadata["evaluation"] = eval_info
        logger.info("orchestrator.done")
        await self._emit("task.completed", task_id=task_id, report=report.model_dump())
        return report

    async def _emit(self, event: str, **kwargs: Any) -> None:
        if self.event_bus is not None:
            await self.event_bus.emit(event, **kwargs)

    async def plan_only(self, user_task: str) -> Task:
        return await self.planner.run(user_task)

    async def execute_plan(self, plan: Task) -> list[AgentOutput]:
        return await self.dag_executor.run(plan)


__all__ = ["Orchestrator"]
