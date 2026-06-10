"""Specialized LLM agents that compose the MARES pipeline."""

from mares.agents.base_agent import BaseAgent
from mares.agents.critic_agent import CriticAgent
from mares.agents.execution_agent import ExecutionAgent
from mares.agents.planner_agent import PlannerAgent
from mares.agents.research_agent import ResearchAgent
from mares.agents.synthesizer_agent import SynthesizerAgent

__all__ = [
    "BaseAgent",
    "PlannerAgent",
    "ResearchAgent",
    "ExecutionAgent",
    "CriticAgent",
    "SynthesizerAgent",
]
