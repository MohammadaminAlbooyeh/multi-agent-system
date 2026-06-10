"""Unit tests for the memory subsystem."""

from __future__ import annotations

import pytest

from mares.memory.agent_memory import AgentMemory
from mares.memory.shared_memory import SharedMemory
from mares.models.agent_output import AgentOutput


def test_agent_memory_stores_history():
    mem = AgentMemory(agent_name="test")
    mem.add("user", "hello")
    mem.add("assistant", "hi")
    assert len(mem) == 2
    history = mem.history()
    assert history[0]["role"] == "user"
    assert history[1]["content"] == "hi"


def test_agent_memory_state():
    mem = AgentMemory(agent_name="test")
    mem.set_state("foo", 42)
    assert mem.get_state("foo") == 42
    assert mem.get_state("missing", "default") == "default"


@pytest.mark.asyncio
async def test_shared_memory_store_and_get_output():
    sm = SharedMemory()
    out = AgentOutput(agent="research_agent", sub_task_id=7, content={"summary": "ok"})
    await sm.store_output(out)
    assert await sm.get_output(7) == out
    outputs = await sm.get_outputs([7, 99])
    assert outputs == [out]


@pytest.mark.asyncio
async def test_shared_memory_snapshot():
    sm = SharedMemory()
    await sm.set("k", "v")
    snap = await sm.snapshot()
    assert snap["kv"]["k"] == "v"


@pytest.mark.asyncio
async def test_shared_memory_clear():
    sm = SharedMemory()
    await sm.set("k", "v")
    await sm.clear()
    assert await sm.get("k") is None
