"""Custom exception hierarchy for MARES."""

from __future__ import annotations


class MARESError(Exception):
    """Base class for all MARES-specific errors."""


class AgentError(MARESError):
    """Base class for agent-level errors."""


class PlanningError(AgentError):
    """Raised when the Planner produces an invalid task graph."""


class ResearchError(AgentError):
    """Raised when the Research Agent fails to produce a valid finding."""


class ToolError(MARESError):
    """Raised when a tool invocation fails (timeout, HTTP error, etc.)."""


class CriticError(AgentError):
    """Raised when the Critic Agent produces an invalid report."""


class ValidationError(MARESError):
    """Raised by input validators."""


__all__ = [
    "MARESError",
    "AgentError",
    "PlanningError",
    "ResearchError",
    "ToolError",
    "CriticError",
    "ValidationError",
]
