"""Groq LLM adapter — fast inference via the OpenAI-compatible API."""

from __future__ import annotations

import os
from typing import Any

from mares.utils.logger import get_logger

logger = get_logger(__name__)


class GroqLLM:
    """Async wrapper for Groq. Uses the OpenAI-compatible client under the hood."""

    def __init__(self, model: str = "llama-3.1-70b-versatile", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self._client: Any | None = None
        if not self.api_key:
            logger.warning("groq_llm.missing_key")

    def _ensure_client(self) -> Any:
        if self._client is None:
            try:
                from openai import AsyncOpenAI  # type: ignore
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "openai package not installed. Run `pip install openai`."
                ) from exc
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1",
            )
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


__all__ = ["GroqLLM"]
