"""Unit tests for the tool layer."""

from __future__ import annotations

import pytest

from mares.tools.file_tool import FileTool
from mares.tools.python_executor_tool import PythonExecutorTool
from mares.tools.search_tool import SearchTool
from mares.tools.tool_registry import ToolRegistry
from mares.utils.exceptions import ToolError


def test_registry_register_and_get():
    reg = ToolRegistry()

    async def my_tool(x: int) -> int:
        return x * 2

    reg.register("double", my_tool, description="double an int")
    assert "double" in reg.list_tools()
    assert reg.get("double") is my_tool


def test_registry_rejects_duplicates():
    reg = ToolRegistry()

    async def t() -> None:
        pass

    reg.register("t", t)
    with pytest.raises(ToolError):
        reg.register("t", t)


@pytest.mark.asyncio
async def test_search_tool_mock_provider():
    tool = SearchTool(provider="mock")
    results = await tool(query="celery", num_results=3)
    assert len(results) == 3
    assert all("title" in r for r in results)


def test_search_tool_parses_duckduckgo_results():
    html = """
    <html><body>
      <div class="result">
        <a class="result__a" href="https://docs.celeryq.dev/en/stable/">
          Celery documentation
        </a>
        <a class="result__snippet">Distributed task queue docs.</a>
      </div>
      <div class="result">
        <a class="result__a"
           href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fgithub.com%2Fcelery%2Fcelery">
          celery/celery
        </a>
        <a class="result__snippet">Distributed Task Queue.</a>
      </div>
    </body></html>
    """
    results = SearchTool._parse_duckduckgo_html(html, 5)
    assert len(results) == 2
    assert results[0]["url"] == "https://docs.celeryq.dev/en/stable/"
    assert results[1]["url"] == "https://github.com/celery/celery"


@pytest.mark.asyncio
async def test_search_tool_duckduckgo_provider(monkeypatch):
    tool = SearchTool(provider="duckduckgo")
    calls = {}

    async def fake_ddg(query: str, n: int):
        calls["args"] = (query, n)
        return [
            {"title": "Result", "url": "https://example.org", "snippet": "ok"}
        ]

    monkeypatch.setattr(tool, "_duckduckgo_search", fake_ddg)
    results = await tool(query="python", num_results=1)
    assert calls["args"] == ("python", 1)
    assert results[0]["url"] == "https://example.org"


@pytest.mark.asyncio
async def test_search_tool_rejects_empty_query():
    tool = SearchTool(provider="mock")
    with pytest.raises(ToolError):
        await tool(query="   ")


@pytest.mark.asyncio
async def test_python_executor_runs_code():
    tool = PythonExecutorTool(default_timeout=5)
    result = await tool.run(code="print(2 + 2)")
    assert result["success"] is True
    assert "4" in result["stdout"]


@pytest.mark.asyncio
async def test_python_executor_timeout():
    tool = PythonExecutorTool(default_timeout=0.5)
    result = await tool.run(code="import time; time.sleep(5)")
    assert result["success"] is False
    assert "timed out" in result["stderr"]


@pytest.mark.asyncio
async def test_file_tool_roundtrip(tmp_path):
    tool = FileTool(root=tmp_path)
    write = await tool.write_file("hello.txt", "hi!")
    assert write["bytes"] == 3
    content = await tool.read_file("hello.txt")
    assert content == "hi!"
    files = await tool.list_files()
    assert "hello.txt" in files


@pytest.mark.asyncio
async def test_file_tool_blocks_path_traversal(tmp_path):
    tool = FileTool(root=tmp_path)
    with pytest.raises(ToolError):
        await tool.read_file("../escape.txt")
