"""Shared memory — global state visible to all agents in a run."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from typing import Any

from mares.models.agent_output import AgentOutput
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class SharedMemory:
    """Thread-safe (asyncio-lock) key/value store + agent-output index.

    All agents read/write the same instance. Output is indexed by
    ``sub_task_id`` so dependents can fetch upstream results quickly.

    Optionally persists to a :class:`MemoryStore` if provided.
    """

    def __init__(self, memory_store: Any | None = None) -> None:
        self._lock = asyncio.Lock()
        self._kv: dict[str, Any] = {}
        self._by_subtask: dict[int, AgentOutput] = {}
        self._store = memory_store

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            self._kv[key] = value
        if self._store is not None:
            await self._store.set(key, value)

    async def get(self, key: str, default: Any = None) -> Any:
        async with self._lock:
            return self._kv.get(key, default)

    async def store_output(self, output: AgentOutput) -> None:
        async with self._lock:
            self._by_subtask[output.sub_task_id] = output
            self._kv.setdefault("outputs", []).append(output)
        if self._store is not None:
            await self._store.set(f"output:{output.sub_task_id}", output.model_dump())
        logger.debug("shared_memory.stored", sub_task_id=output.sub_task_id)

    async def get_output(self, sub_task_id: int) -> AgentOutput | None:
        async with self._lock:
            return self._by_subtask.get(sub_task_id)

    async def get_outputs(self, sub_task_ids: Iterable[int]) -> list[AgentOutput]:
        async with self._lock:
            return [self._by_subtask[i] for i in sub_task_ids if i in self._by_subtask]

    async def all_outputs(self) -> list[AgentOutput]:
        async with self._lock:
            return list(self._kv.get("outputs", []))

    async def snapshot(self) -> dict[str, Any]:
        async with self._lock:
            return {
                "kv": dict(self._kv),
                "by_subtask": dict(self._by_subtask),
            }

    async def clear(self) -> None:
        async with self._lock:
            self._kv.clear()
            self._by_subtask.clear()
        if self._store is not None:
            await self._store.clear()


__all__ = ["SharedMemory"]
