"""Task model — top-level user task that contains a DAG of sub-tasks."""

from __future__ import annotations

from pydantic import BaseModel, Field

from mares.models.sub_task import SubTask


class Task(BaseModel):
    """A user-supplied task and the planner's decomposition into sub-tasks."""

    description: str = Field(..., min_length=1)
    sub_tasks: list[SubTask] = Field(default_factory=list)

    def sub_task_ids(self) -> list[int]:
        return [st.id for st in self.sub_tasks]


__all__ = ["Task"]
