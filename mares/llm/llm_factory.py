"""LLM Factory — return a configured LLM adapter based on env / settings."""

from __future__ import annotations

import os
from typing import Any

from mares.llm.claude_llm import ClaudeLLM
from mares.llm.groq_llm import GroqLLM
from mares.llm.local_llm import LocalLLM
from mares.llm.openai_llm import OpenAILLM
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class LLMFactory:
    """Resolves the active LLM provider lazily.

    A factory instance can produce multiple underlying adapters — agents
    can request specific providers by name. The default provider is read
    from the ``DEFAULT_LLM_PROVIDER`` env var.
    """

    SUPPORTED = {"openai", "anthropic", "groq", "ollama", "local"}

    def __init__(self, default_provider: str | None = None, default_model: str | None = None) -> None:
        self.default_provider = (default_provider or os.getenv("DEFAULT_LLM_PROVIDER", "openai")).lower()
        self.default_model = default_model or os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
        if self.default_provider not in self.SUPPORTED:
            raise ValueError(
                f"Unsupported LLM provider: {self.default_provider}. "
                f"Choose from {sorted(self.SUPPORTED)}."
            )
        self._cache: dict[str, Any] = {}

    def get(self, provider: str | None = None, model: str | None = None) -> Any:
        provider = (provider or self.default_provider).lower()
        model = model or self.default_model
        key = f"{provider}:{model}"
        if key in self._cache:
            return self._cache[key]
        adapter = self._build(provider, model)
        self._cache[key] = adapter
        return adapter

    def _build(self, provider: str, model: str) -> Any:
        logger.info("llm_factory.build", provider=provider, model=model)
        if provider == "openai":
            return OpenAILLM(model=model)
        if provider == "anthropic":
            return ClaudeLLM(model=model)
        if provider == "groq":
            return GroqLLM(model=model)
        if provider in {"ollama", "local"}:
            return LocalLLM(model=model)
        raise ValueError(f"Unknown provider: {provider}")

    async def generate(
        self,
        system: str,
        user: str,
        provider: str | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        adapter = self.get(provider, model)
        return await adapter.generate(system=system, user=user, **kwargs)


__all__ = ["LLMFactory"]
