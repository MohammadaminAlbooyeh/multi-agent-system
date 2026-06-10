"""Tool configuration block — timeouts, API keys, sandbox limits."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolConfig:
    search_timeout_seconds: int
    search_api_key: str | None
    python_sandbox_timeout_seconds: int
    tool_failure_rate: float


def load_tool_config() -> ToolConfig:
    return ToolConfig(
        search_timeout_seconds=int(os.getenv("SEARCH_TIMEOUT_SECONDS", "30")),
        search_api_key=os.getenv("SERPAPI_API_KEY") or None,
        python_sandbox_timeout_seconds=int(os.getenv("PYTHON_SANDBOX_TIMEOUT_SECONDS", "10")),
        tool_failure_rate=float(os.getenv("TOOL_FAILURE_RATE", "0.0")),
    )


__all__ = ["ToolConfig", "load_tool_config"]
