"""Anthropic Claude LLM adapter."""

from __future__ import annotations

import os
from typing import Any

from mares.utils.logger import get_logger

logger = get_logger(__name__)


class ClaudeLLM:
    """Async wrapper around the official Anthropic SDK."""

    def __init__(self, model: str = "claude-3-5-sonnet-latest", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._client: Any | None = None
        if not self.api_key:
            logger.warning("claude_llm.missing_key")

    def _ensure_client(self) -> Any:
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic  # type: ignore
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "anthropic package not installed. Run `pip install anthropic`."
                ) from exc
            self._client = AsyncAnthropic(api_key=self.api_key)
        return self._client

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        **_: Any,
    ) -> str:
        client = self._ensure_client()
        response = await client.messages.create(
            model=self.model,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": user}],
        )
        # Concatenate text blocks.
        return "".join(
            block.text for block in response.content if getattr(block, "type", "") == "text"
        )


__all__ = ["ClaudeLLM"]
