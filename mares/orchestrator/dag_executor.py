"""DAG Executor — build dependency graph, topologically sort, run in waves."""

from __future__ import annotations

from typing import Iterable

from mares.agents.execution_agent import ExecutionAgent
from mares.agents.research_agent import ResearchAgent
from mares.graph.dag import DAG
from mares.graph.dependency_resolver import DependencyResolver
from mares.graph.task_node import TaskNode
from mares.models.agent_output import AgentOutput
from mares.models.sub_task import SubTask
from mares.models.task import Task
from mares.orchestrator.parallel_runner import ParallelRunner
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class DAGExecutor:
    """Executes a :class:`Task` (which contains sub-tasks + dependencies).

    Steps:
        1. Build a :class:`DAG` from the planner output.
        2. Topologically sort and group by execution "wave" (level).
        3. Run each wave in parallel via :class:`ParallelRunner`, tracking
           execution state with :class:`TaskNode`.
    """

    def __init__(
        self,
        research_agent: ResearchAgent,
        execution_agent: ExecutionAgent | None = None,
        max_concurrency: int = 5,
    ) -> None:
        self.research_agent = research_agent
        self.execution_agent = execution_agent
        self.runner = ParallelRunner(max_concurrency=max_concurrency)

    async def run(self, task: Task) -> list[AgentOutput]:
        dag = self._build_dag(task.sub_tasks)
        resolver = DependencyResolver(dag)
        waves = resolver.execution_waves()

        # Build TaskNode index for runtime state tracking
        self._task_nodes: dict[int, TaskNode] = {
            st.id: TaskNode(sub_task=st)
            for st in task.sub_tasks
        }

        logger.info("dag_executor.start", waves=len(waves), nodes=dag.node_count())

        all_outputs: list[AgentOutput] = []
        for level, wave in enumerate(waves):
            logger.info("dag_executor.wave", level=level, size=len(wave))
            # Mark tasks as running
            for st in wave:
                if st.id in self._task_nodes:
                    self._task_nodes[st.id].mark_running()
            outputs = await self.runner.run_wave(wave, self._dispatch_subtask)
            # Mark results
            for out in outputs:
                if out.sub_task_id in self._task_nodes:
                    node = self._task_nodes[out.sub_task_id]
                    node.mark_done(out)
            all_outputs.extend(outputs)

        logger.info("dag_executor.done", outputs=len(all_outputs))
        return all_outputs

    def _build_dag(self, sub_tasks: Iterable[SubTask]) -> DAG:
        dag: DAG = DAG()
        for st in sub_tasks:
            dag.add_node(st.id, data=st)
            for dep in st.depends_on:
                dag.add_edge(dep, st.id)
        return dag

    async def _dispatch_subtask(self, sub_task: SubTask) -> AgentOutput:
        """Decide whether the sub-task needs research, code execution, or both.

        A very simple heuristic: if the description contains 'code'/'implement'/
        'algorithm'/'script' we run the ExecutionAgent, otherwise Research.
        """
        lowered = sub_task.task.lower()
        needs_code = any(
            kw in lowered
            for kw in ("code", "implement", "algorithm", "script", "function")
        )

        if needs_code and self.execution_agent is not None:
            result = await self.execution_agent.run(sub_task)
            return AgentOutput(
                agent="execution_agent",
                sub_task_id=sub_task.id,
                content=result.model_dump(),
                metadata={"language": result.language, "success": result.success},
            )

        finding = await self.research_agent.run(sub_task)
        return AgentOutput(
            agent="research_agent",
            sub_task_id=sub_task.id,
            content={
                "summary": finding.summary,
                "facts": finding.facts,
            },
            metadata={"sources": finding.sources},
        )


__all__ = ["DAGExecutor"]
