"""Message schema for inter-agent communication."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

MessageType = Literal["task", "result", "status", "error", "broadcast"]


class Message(BaseModel):
    """A single async message exchanged between agents (or via the bus)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = "task"
    sender: str
    recipient: str | None = None  # None => broadcast
    topic: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def is_broadcast(self) -> bool:
        return self.recipient is None


__all__ = ["Message", "MessageType"]
