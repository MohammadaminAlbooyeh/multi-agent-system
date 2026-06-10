"""Self-correction loop — re-runs failed sub-tasks when the Critic rejects them."""

from __future__ import annotations

from typing import Any

from mares.agents.critic_agent import CriticAgent
from mares.models.agent_output import AgentOutput
from mares.models.task import Task
from mares.orchestrator.dag_executor import DAGExecutor
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class SelfCorrectionLoop:
    """Wraps a :class:`DAGExecutor` and re-runs on critic failure.

    Strategy:
        1. Execute the plan.
        2. Pass outputs to the critic.
        3. If critic.passed is False, identify failing sub-task IDs and
           re-execute just those (up to ``max_retries`` times).
    """

    def __init__(
        self,
        dag_executor: DAGExecutor,
        critic: CriticAgent,
        max_retries: int = 3,
    ) -> None:
        self.dag_executor = dag_executor
        self.critic = critic
        self.max_retries = max_retries

    async def run(self, task: Task) -> list[AgentOutput]:
        outputs = await self.dag_executor.run(task)

        for attempt in range(1, self.max_retries + 1):
            report = await self.critic.run(outputs)
            if report.passed:
                logger.info("self_correction.passed", attempt=attempt)
                return outputs

            failed_ids = {issue.get("sub_task_id") for issue in report.issues}
            failed_ids.discard(None)
            logger.warning(
                "self_correction.retry",
                attempt=attempt,
                failed=sorted(failed_ids),
            )
            outputs = await self._rerun_failed(task, outputs, failed_ids)

        # Final attempt — run the critic one more time, return what we have.
        final = await self.critic.run(outputs)
        logger.warning("self_correction.exhausted", passed=final.passed)
        return outputs

    async def _rerun_failed(
        self,
        task: Task,
        previous_outputs: list[AgentOutput],
        failed_ids: set[int],
    ) -> list[AgentOutput]:
        """Replace outputs for the failed sub-tasks with fresh runs."""
        if not failed_ids:
            return previous_outputs

        # Build a tiny sub-plan containing only the failed sub-tasks.
        failed_subtasks = [st for st in task.sub_tasks if st.id in failed_ids]
        sub_plan = Task(description=task.description, sub_tasks=failed_subtasks)
        new_outputs = await self.dag_executor.run(sub_plan)

        # Merge: replace by sub_task_id, keep everything else.
        by_id = {out.sub_task_id: out for out in new_outputs}
        merged: list[AgentOutput] = []
        seen: set[int] = set()
        for out in previous_outputs:
            if out.sub_task_id in by_id:
                merged.append(by_id[out.sub_task_id])
                seen.add(out.sub_task_id)
            else:
                merged.append(out)
        # Append any new outputs that weren't in the previous batch.
        for out in new_outputs:
            if out.sub_task_id not in seen:
                merged.append(out)
        return merged


__all__ = ["SelfCorrectionLoop"]
