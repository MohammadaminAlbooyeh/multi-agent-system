"""LLM configuration block — provider, model, and per-provider keys."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    api_key: str | None = None
    base_url: str | None = None


def load_llm_config() -> LLMConfig:
    provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()
    model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")

    api_key: str | None
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
    elif provider in {"ollama", "local"}:
        api_key = None
    else:
        api_key = None

    return LLMConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=os.getenv("OLLAMA_BASE_URL") if provider in {"ollama", "local"} else None,
    )


__all__ = ["LLMConfig", "load_llm_config"]
