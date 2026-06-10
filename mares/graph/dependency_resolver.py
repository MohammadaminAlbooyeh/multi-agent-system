"""Dependency resolver — turns a DAG into a list of execution waves."""

from __future__ import annotations

from mares.graph.dag import DAG
from mares.graph.task_node import TaskNode
from mares.models.sub_task import SubTask
from mares.utils.exceptions import PlanningError
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class DependencyResolver:
    """Wraps a :class:`DAG` and produces execution plans."""

    def __init__(self, dag: DAG) -> None:
        self.dag = dag

    def execution_waves(self) -> list[list[SubTask]]:
        """Return a list of waves; each wave is a list of :class:`SubTask`."""
        levels = self.dag.levels()
        waves: list[list[SubTask]] = []
        for level_ids in levels:
            waves.append([self.dag.get(n) for n in level_ids])
        logger.info("dependency_resolver.waves", count=len(waves))
        return waves

    def task_nodes(self) -> dict[int, TaskNode]:
        out: dict[int, TaskNode] = {}
        for node_id in self.dag.nodes():
            sub_task: SubTask = self.dag.get(node_id)
            out[node_id] = TaskNode(sub_task=sub_task)
        return out

    def validate(self) -> None:
        """Ensure the DAG has no cycles and at least one node."""
        if self.dag.node_count() == 0:
            raise PlanningError("Cannot resolve an empty DAG.")
        # ``topological_sort`` will raise if there's a cycle.
        self.dag.topological_sort()


__all__ = ["DependencyResolver"]
