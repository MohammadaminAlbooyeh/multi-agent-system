# Memory

MARES has a two-tier memory system.

## Per-agent memory

`mares.memory.agent_memory.AgentMemory` is a bounded deque of
`{role, content, ...}` messages plus a `dict` of arbitrary state.
Each agent owns one instance and uses it for context-window continuity.

## Shared memory

`mares.memory.shared_memory.SharedMemory` is a single async-safe
key/value store used by the whole run. Agent outputs are indexed by
`sub_task_id` so dependents can fetch upstream results in O(1).

## Persistent store

`mares.memory.memory_store.MemoryStore` is a thin abstraction over either
an in-process dict or a Redis instance. Used for long-term history,
caching, and replays.

```
set MARES_MEMORY_BACKEND=redis
set REDIS_URL=redis://localhost:6379/0
```
