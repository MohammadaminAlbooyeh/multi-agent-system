"""OpenAI LLM adapter (GPT-4 / GPT-4o family)."""

from __future__ import annotations

import os
from typing import Any

from mares.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAILLM:
    """Async wrapper around the official OpenAI Python SDK."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._client: Any | None = None
        if not self.api_key:
            logger.warning("openai_llm.missing_key")

    def _ensure_client(self) -> Any:
        if self._client is None:
            try:
                from openai import AsyncOpenAI  # type: ignore
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "openai package not installed. Run `pip install openai`."
                ) from exc
            self._client = AsyncOpenAI(api_key=self.api_key)
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
        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""


__all__ = ["OpenAILLM"]
