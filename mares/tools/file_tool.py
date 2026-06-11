"""File tool — read, write, list files in a sandboxed working directory."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mares.tools.tool_registry import default_registry
from mares.utils.exceptions import ToolError
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class FileTool:
    """File I/O restricted to a single root directory.

    All paths are resolved relative to ``root`` and rejected if they escape
    it (no `..` traversal).
    """

    name = "file"
    description = "Read, write, and list files within a sandboxed directory."

    def __init__(self, root: str | os.PathLike[str] = ".") -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, path: str) -> Path:
        candidate = (self.root / path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ToolError(f"Path '{path}' escapes the file root.") from exc
        return candidate

    async def read_file(self, path: str, **_: Any) -> str:
        p = self._resolve(path)
        if not p.is_file():
            raise ToolError(f"File not found: {path}")
        return p.read_text(encoding="utf-8", errors="replace")

    async def write_file(self, path: str, content: str, **_: Any) -> dict[str, Any]:
        p = self._resolve(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"path": str(p.relative_to(self.root)), "bytes": len(content)}

    async def list_files(self, directory: str = ".", **_: Any) -> list[str]:
        p = self._resolve(directory)
        if not p.is_dir():
            raise ToolError(f"Not a directory: {directory}")
        return sorted(
            str(child.relative_to(self.root))
            for child in p.rglob("*")
            if child.is_file()
        )

    async def __call__(self, action: str, **kwargs: Any) -> Any:
        action = action.lower()
        if action == "read":
            return await self.read_file(**kwargs)
        if action == "write":
            return await self.write_file(**kwargs)
        if action == "list":
            return await self.list_files(**kwargs)
        raise ToolError(f"Unknown file action: {action!r}")


# Auto-register on import.
default_registry.register(
    FileTool.name,
    FileTool().__call__,
    description=FileTool.description,
    schema={"action": "read|write|list", "path": "string", "content": "string"},
)

__all__ = ["FileTool"]
