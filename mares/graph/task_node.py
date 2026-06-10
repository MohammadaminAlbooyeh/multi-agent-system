"""TaskNode — payload for a single node in the DAG."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from mares.models.sub_task import SubTask


class TaskNode(BaseModel):
    """A node in the MARES DAG.

    Wraps a :class:`SubTask` with extra runtime metadata (status, attempts,
    result, error).
    """

    sub_task: SubTask
    status: str = Field(default="pending")  # pending | running | done | failed
    attempts: int = 0
    result: Any | None = None
    error: str | None = None

    def mark_running(self) -> None:
        self.status = "running"
        self.attempts += 1

    def mark_done(self, result: Any) -> None:
        self.status = "done"
        self.result = result
        self.error = None

    def mark_failed(self, error: str) -> None:
        self.status = "failed"
        self.error = error


__all__ = ["TaskNode"]
