"""JSON parsing helpers — extract JSON from messy LLM outputs."""

from __future__ import annotations

import json
import re
from typing import Any

from mares.utils.exceptions import MARESError


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)
_ARRAY_RE = re.compile(r"\[.*\]", re.DOTALL)


class JSONDecodeError(MARESError):
    """Raised when JSON cannot be recovered from a string."""


def safe_json_loads(text: str) -> Any:
    """Try hard to extract a JSON value from a string.

    Strategy:
        1. Direct ``json.loads``.
        2. Strip ```json ... ``` fences.
        3. Pull the first {...} or [...] block.
    """
    if not text:
        raise JSONDecodeError("Empty string.")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fence = _FENCE_RE.search(text)
    if fence:
        try:
            return json.loads(fence.group(1))
        except json.JSONDecodeError:
            pass

    for pattern in (_OBJECT_RE, _ARRAY_RE):
        match = pattern.search(text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                continue

    raise JSONDecodeError(f"Could not parse JSON from: {text[:120]}...")


__all__ = ["safe_json_loads", "JSONDecodeError"]
