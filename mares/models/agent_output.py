"""AgentOutput — generic envelope for any agent's response."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    """Standard wrapper around an agent's output."""

    agent: str
    sub_task_id: int
    content: Any
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


__all__ = ["AgentOutput"]
