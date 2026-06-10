"""Pydantic request/response models for the MARES API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    task: str = Field(..., min_length=1, description="High-level user task.")


class TaskGraph(BaseModel):
    id: int
    task: str
    depends_on: list[int] = Field(default_factory=list)


class PlanResponse(BaseModel):
    task: str
    sub_tasks: list[TaskGraph]


class RunRequest(BaseModel):
    task: str = Field(..., min_length=1)


class RunResponse(BaseModel):
    task_id: str
    status: str
    task: str


class StatusResponse(BaseModel):
    task_id: str
    status: str
    error: str | None = None
    report: dict | None = None


__all__ = [
    "PlanRequest",
    "PlanResponse",
    "TaskGraph",
    "RunRequest",
    "RunResponse",
    "StatusResponse",
]
