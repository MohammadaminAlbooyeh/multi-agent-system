"""Cost controller — enforce per-agent (and global) token budgets."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from mares.utils.exceptions import MARESError
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class TokenBudgetExceeded(MARESError):
    """Raised when an agent exceeds its configured token budget."""


@dataclass
class CostController:
    """Track token usage and enforce per-agent limits.

    Token usage is *estimated* — adapters must call :meth:`record` after
    each LLM call with the actual input/output token counts from the
    response. If an adapter doesn't report counts, the cost controller
    assumes a pessimistic default of 1 token per 4 characters.
    """

    per_agent_budgets: dict[str, int] = field(default_factory=dict)
    global_budget: int = 0
    _per_agent_used: dict[str, int] = field(default_factory=dict)
    _global_used: int = 0

    @classmethod
    def from_env(cls) -> "CostController":
        return cls(
            per_agent_budgets={
                "planner_agent": int(os.getenv("TOKEN_BUDGET_PLANNER", "8000")),
                "research_agent": int(os.getenv("TOKEN_BUDGET_RESEARCH", "12000")),
                "execution_agent": int(os.getenv("TOKEN_BUDGET_EXECUTION", "8000")),
                "critic_agent": int(os.getenv("TOKEN_BUDGET_CRITIC", "6000")),
                "synthesizer_agent": int(os.getenv("TOKEN_BUDGET_SYNTHESIZER", "10000")),
            },
            global_budget=int(os.getenv("TOKEN_BUDGET_GLOBAL", "50000")),
        )

    def record(self, agent: str, input_tokens: int, output_tokens: int) -> None:
        total = max(input_tokens, 0) + max(output_tokens, 0)
        self._per_agent_used[agent] = self._per_agent_used.get(agent, 0) + total
        self._global_used += total
        logger.info(
            "cost_controller.record",
            agent=agent,
            used=self._per_agent_used[agent],
            global_used=self._global_used,
        )
        self._enforce(agent)

    def estimate(self, agent: str, text: str) -> int:
        """Rough token estimate from a text string."""
        return max(1, len(text) // 4)

    def _enforce(self, agent: str) -> None:
        if self._global_used > self.global_budget > 0:
            raise TokenBudgetExceeded(
                f"Global token budget exhausted ({self._global_used} > {self.global_budget})."
            )
        budget = self.per_agent_budgets.get(agent, 0)
        used = self._per_agent_used.get(agent, 0)
        if budget and used > budget:
            raise TokenBudgetExceeded(
                f"Agent '{agent}' exceeded its budget ({used} > {budget})."
            )

    def estimate_and_record(self, agent: str, input_text: str, output_text: str) -> None:
        in_tokens = self.estimate(agent, input_text)
        out_tokens = self.estimate(agent, output_text)
        self.record(agent, in_tokens, out_tokens)

    def snapshot(self) -> dict[str, Any]:
        return {
            "global_used": self._global_used,
            "per_agent_used": dict(self._per_agent_used),
        }


__all__ = ["CostController", "TokenBudgetExceeded"]
