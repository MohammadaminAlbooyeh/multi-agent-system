"""ExecutionResult — output of the Execution Agent / Python sandbox."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExecutionResult(BaseModel):
    """Outcome of running a generated code snippet."""

    sub_task_id: int
    language: str = "python"
    code: str = ""
    stdout: str = ""
    stderr: str = ""
    return_code: int = -1
    success: bool = False
    metadata: dict[str, str] = Field(default_factory=dict)


__all__ = ["ExecutionResult"]
