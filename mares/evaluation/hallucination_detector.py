"""Hallucination detection — surface claims that lack supporting sources."""

from __future__ import annotations

import re
from typing import Any

from mares.utils.logger import get_logger

logger = get_logger(__name__)


class HallucinationDetector:
    """Heuristic detector: flags sentences with concrete claims but no sources.

    Real production systems should use a stronger method (NLI, retrieval
    grounding, or an LLM-as-judge). This is a fast, dependency-free
    baseline used in the self-correction loop.
    """

    CLAIM_PATTERNS = [
        r"\b\d{4}\b",  # years
        r"\baccording to\b",
        r"\bstudies show\b",
        r"\bresearch suggests\b",
        r"\bit is known that\b",
    ]

    def __init__(self, require_sources: bool = True) -> None:
        self.require_sources = require_sources
        self._patterns = [re.compile(p, re.IGNORECASE) for p in self.CLAIM_PATTERNS]

    def detect(
        self,
        text: str,
        sources: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        sources = sources or []
        flagged: list[dict[str, Any]] = []
        for sentence in self._split_sentences(text):
            has_claim = any(p.search(sentence) for p in self._patterns)
            if has_claim and (self.require_sources and not sources):
                flagged.append(
                    {
                        "sentence": sentence,
                        "reason": "claim_without_sources",
                    }
                )
        logger.debug("hallucination_detector.flagged", count=len(flagged))
        return flagged

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


__all__ = ["HallucinationDetector"]
