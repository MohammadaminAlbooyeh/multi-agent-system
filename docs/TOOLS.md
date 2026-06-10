# Tools

Tools are async callables registered in `mares.tools.tool_registry.ToolRegistry`.

## Built-in tools

| Tool | Module | Used by |
|------|--------|---------|
| `search` | `search_tool.py` | Research Agent |
| `python_executor` | `python_executor_tool.py` | Execution Agent |
| `file` | `file_tool.py` | Research + Execution |
| `api_call` | `api_call_tool.py` | Research Agent |
| (failure sim) | `tool_failure_simulator.py` | Testing |

## Registering a custom tool

```python
from mares.tools.tool_registry import default_registry

async def my_tool(query: str) -> dict:
    return {"answer": 42}

default_registry.register(
    "my_tool",
    my_tool,
    description="Answer the question.",
    schema={"query": "string"},
)
```

## Executing a tool

```python
from mares.tools.tool_executor import ToolExecutor

executor = ToolExecutor(default_timeout=15)
result = await executor.execute("my_tool", query="Why?")
```

The `ToolExecutor` adds:

- **Timeout** — `asyncio.wait_for` with a configurable limit.
- **Retries** — exponential backoff (configurable).
- **Error wrapping** — converts raw exceptions to `ToolError`.
