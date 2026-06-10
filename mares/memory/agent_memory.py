"""Per-agent context memory — conversation history + task-specific state."""

from __future__ import annotations

from collections import deque
from typing import Any, Deque

from mares.utils.logger import get_logger

logger = get_logger(__name__)


class AgentMemory:
    """Bounded conversation history for a single agent.

    Stores a deque of ``{role, content, ...}`` messages. The default
    capacity is generous (1000) but callers can configure it.
    """

    def __init__(self, agent_name: str, capacity: int = 1000) -> None:
        self.agent_name = agent_name
        self.capacity = capacity
        self._messages: Deque[dict[str, Any]] = deque(maxlen=capacity)
        self._state: dict[str, Any] = {}

    def add(self, role: str, content: str, **extras: Any) -> None:
        msg = {"role": role, "content": content, **extras}
        self._messages.append(msg)

    def history(self) -> list[dict[str, Any]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()
        self._state.clear()

    def set_state(self, key: str, value: Any) -> None:
        self._state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def __len__(self) -> int:
        return len(self._messages)


__all__ = ["AgentMemory"]
