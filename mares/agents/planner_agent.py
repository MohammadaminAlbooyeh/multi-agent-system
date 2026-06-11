"""Planner Agent — decomposes the user task into a DAG of sub-tasks."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import ValidationError

from mares.agents.base_agent import BaseAgent
from mares.models.sub_task import SubTask
from mares.models.task import Task
from mares.utils.exceptions import PlanningError
from mares.utils.json_utils import JSONDecodeError, safe_json_loads
from mares.utils.logger import get_logger

logger = get_logger(__name__)


PLANNER_SYSTEM_PROMPT = """You are the MARES Planner Agent.
Your job is to break a complex user task into a small number of well-defined
sub-tasks and to define the dependencies between them.

Output STRICT JSON with the shape:
{
  "tasks": [
    {"id": 1, "task": "...", "depends_on": []}
  ]
}

Rules:
- IDs are 1-indexed integers.
- `depends_on` lists integer IDs of tasks that must finish before this one.
- Sub-tasks should be small, independent, and collectively exhaustive.
- Return ONLY JSON, no commentary, no markdown fences.
"""


class PlannerAgent(BaseAgent):
    """Receives the main task and returns a :class:`Task` (a graph)."""

    name: ClassVar[str] = "planner_agent"
    description: ClassVar[str] = (
        "Decomposes the main task into sub-tasks and defines a dependency graph."
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(system_prompt=PLANNER_SYSTEM_PROMPT, **kwargs)

    async def run(self, input_data: str) -> Task:
        """Plan a task. ``input_data`` is the user task description."""
        if not isinstance(input_data, str) or not input_data.strip():
            raise PlanningError("Planner requires a non-empty task string.")

        self.remember("user", input_data)
        logger.info("planner.start", task_length=len(input_data))

        raw = await self._generate(
            system=self.system_prompt,
            user=input_data,
        )
        self.remember("assistant", raw)

        try:
            payload = safe_json_loads(raw)
            tasks = [
                SubTask(
                    id=int(item["id"]),
                    task=str(item["task"]),
                    depends_on=list(item.get("depends_on", [])),
                )
                for item in payload.get("tasks", [])
            ]
        except (ValueError, KeyError, TypeError, ValidationError, JSONDecodeError) as exc:
            raise PlanningError(f"Planner produced invalid JSON: {exc}") from exc

        task_graph = Task(description=input_data, sub_tasks=tasks)
        self.validate_output(task_graph)
        logger.info("planner.done", sub_tasks=len(tasks))
        return task_graph


__all__ = ["PlannerAgent", "PLANNER_SYSTEM_PROMPT"]
