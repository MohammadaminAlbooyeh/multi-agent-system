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

## Web search

`SearchTool` performs real searches. Select a backend with `SEARCH_PROVIDER`:

- `auto` (default) — SerpAPI if `SERPAPI_API_KEY` is set, then Brave if
  `BRAVE_API_KEY` is set, otherwise keyless DuckDuckGo.
- `serpapi`, `brave`, `duckduckgo` — force a specific backend.
- `mock` — deterministic fixtures, intended only for tests.

Results are normalised to `{"title", "url", "snippet"}`. A provider failure
raises `ToolError`; the Research Agent catches it and continues without web
context rather than failing the whole sub-task.

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
