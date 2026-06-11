"""Python executor tool — runs Python code in a subprocess sandbox."""

from __future__ import annotations

import asyncio
import os
import tempfile
from typing import Any

from mares.tools.tool_registry import default_registry
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class PythonExecutorTool:
    """Safely runs Python code in a subprocess.

    - Writes code to a temp file.
    - Executes with a hard timeout via :func:`asyncio.wait_for`.
    - Captures stdout / stderr / return code.

    NOTE: This is *not* a hardened sandbox (no seccomp / namespaces). It is
    intended for short, trusted research snippets. For untrusted code, plug
    in a real sandbox (gVisor, Firecracker, Docker --read-only).
    """

    name = "python_executor"
    description = "Run a snippet of Python code and return stdout/stderr/returncode."

    def __init__(self, default_timeout: float = 10.0) -> None:
        self.default_timeout = default_timeout

    async def run(
        self,
        code: str,
        timeout: float | None = None,
        **_: Any,
    ) -> dict[str, Any]:
        timeout = timeout or self.default_timeout
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=tempfile.gettempdir()
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            logger.info("python_executor.start", timeout=timeout, path=tmp_path)
            proc = await asyncio.create_subprocess_exec(
                "python3",
                tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=tempfile.gettempdir(),
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return {
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout}s",
                    "return_code": -1,
                    "success": False,
                }

            stdout = (stdout_b or b"").decode("utf-8", errors="replace")
            stderr = (stderr_b or b"").decode("utf-8", errors="replace")
            return {
                "stdout": stdout,
                "stderr": stderr,
                "return_code": proc.returncode,
                "success": proc.returncode == 0,
            }
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    async def __call__(self, code: str, timeout: float | None = None, **kwargs: Any) -> dict[str, Any]:
        return await self.run(code=code, timeout=timeout, **kwargs)


# Auto-register on import.
default_registry.register(
    PythonExecutorTool.name,
    PythonExecutorTool().__call__,
    description=PythonExecutorTool.description,
    schema={"code": "string", "timeout": "number"},
)

__all__ = ["PythonExecutorTool"]
