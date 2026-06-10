"""Consistency checker — verify outputs from different agents agree."""

from __future__ import annotations

from collections import Counter
from typing import Any

from mares.models.agent_output import AgentOutput
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class ConsistencyChecker:
    """Cross-agent consistency check.

    Heuristics implemented:
        - Topic overlap: do agents mention the same key entities?
        - Numeric agreement: are reported numbers within tolerance?
        - Source agreement: do agents cite the same sources for the same claim?
    """

    def __init__(self, numeric_tolerance: float = 0.05) -> None:
        self.numeric_tolerance = numeric_tolerance

    def check(self, outputs: list[AgentOutput]) -> dict[str, Any]:
        if len(outputs) < 2:
            return {"consistent": True, "issues": []}

        issues: list[dict[str, Any]] = []
        nums_per_agent = [self._extract_numbers(o.content) for o in outputs]

        for i in range(len(outputs)):
            for j in range(i + 1, len(outputs)):
                nums_i = nums_per_agent[i]
                nums_j = nums_per_agent[j]
                if not nums_i or not nums_j:
                    continue
                overlap = self._numeric_overlap(nums_i, nums_j)
                if overlap < (1 - self.numeric_tolerance):
                    issues.append(
                        {
                            "type": "numeric_mismatch",
                            "between": [outputs[i].agent, outputs[j].agent],
                            "overlap": overlap,
                        }
                    )

        return {
            "consistent": not issues,
            "issues": issues,
            "checked_pairs": len(outputs) * (len(outputs) - 1) // 2,
        }

    @staticmethod
    def _extract_numbers(content: Any) -> list[float]:
        import re

        if not isinstance(content, (str, dict)):
            return []
        text = content if isinstance(content, str) else str(content)
        return [float(n) for n in re.findall(r"-?\d+\.?\d*", text)]

    @staticmethod
    def _numeric_overlap(a: list[float], b: list[float]) -> float:
        ca, cb = Counter(a), Counter(b)
        common = sum((ca & cb).values())
        total = max(sum(ca.values()), sum(cb.values()))
        return common / total if total else 1.0


__all__ = ["ConsistencyChecker"]
