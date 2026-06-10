"""Local LLM adapter — talks to an Ollama server running on localhost."""

from __future__ import annotations

import os
from typing import Any

import httpx

from mares.utils.logger import get_logger

logger = get_logger(__name__)


class LocalLLM:
    """Async client for a local Ollama server.

    No SDK dependency — uses :mod:`httpx` directly to call the
    ``/api/chat`` endpoint.
    """

    def __init__(
        self,
        model: str = "llama3.1",
        base_url: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.model = model
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.timeout = timeout

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.2,
        **_: Any,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": temperature},
        }
        url = f"{self.base_url}/api/chat"
        logger.info("local_llm.request", url=url, model=self.model)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        return data.get("message", {}).get("content", "")


__all__ = ["LocalLLM"]
