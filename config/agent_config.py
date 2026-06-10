"""Per-agent configuration (model + token budget)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentConfig:
    name: str
    model: str
    token_budget: int
    temperature: float = 0.2
    max_tokens: int = 1024


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def load_agent_configs() -> dict[str, AgentConfig]:
    return {
        "planner_agent": AgentConfig(
            name="planner_agent",
            model=_env("LLM_MODEL_PLANNER", _env("DEFAULT_LLM_MODEL", "gpt-4o-mini")),
            token_budget=int(_env("TOKEN_BUDGET_PLANNER", "8000")),
        ),
        "research_agent": AgentConfig(
            name="research_agent",
            model=_env("LLM_MODEL_RESEARCH", _env("DEFAULT_LLM_MODEL", "gpt-4o-mini")),
            token_budget=int(_env("TOKEN_BUDGET_RESEARCH", "12000")),
        ),
        "execution_agent": AgentConfig(
            name="execution_agent",
            model=_env("LLM_MODEL_EXECUTION", _env("DEFAULT_LLM_MODEL", "gpt-4o-mini")),
            token_budget=int(_env("TOKEN_BUDGET_EXECUTION", "8000")),
        ),
        "critic_agent": AgentConfig(
            name="critic_agent",
            model=_env("LLM_MODEL_CRITIC", _env("DEFAULT_LLM_MODEL", "gpt-4o-mini")),
            token_budget=int(_env("TOKEN_BUDGET_CRITIC", "6000")),
        ),
        "synthesizer_agent": AgentConfig(
            name="synthesizer_agent",
            model=_env("LLM_MODEL_SYNTHESIZER", _env("DEFAULT_LLM_MODEL", "gpt-4o-mini")),
            token_budget=int(_env("TOKEN_BUDGET_SYNTHESIZER", "10000")),
        ),
    }


__all__ = ["AgentConfig", "load_agent_configs"]
