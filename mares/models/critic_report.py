"""CriticReport — output of the Critic Agent."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high"]


class CriticIssue(BaseModel):
    sub_task_id: int | None = None
    severity: Severity = "low"
    description: str


class CriticReport(BaseModel):
    passed: bool = False
    issues: list[CriticIssue] = Field(default_factory=list)
    summary: str = ""

    def failed_subtask_ids(self) -> set[int]:
        return {i.sub_task_id for i in self.issues if i.sub_task_id is not None}


__all__ = ["CriticReport", "CriticIssue", "Severity"]
