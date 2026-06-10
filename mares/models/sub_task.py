"""SubTask model — a single node in the planner's DAG."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SubTask(BaseModel):
    """One sub-task produced by the Planner Agent."""

    id: int = Field(..., ge=1)
    task: str = Field(..., min_length=1)
    depends_on: list[int] = Field(default_factory=list)


__all__ = ["SubTask"]
