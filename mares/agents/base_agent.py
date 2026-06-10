"""Abstract base class for all MARES agents."""

from __future__ import annotations

import abc
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from mares.llm.llm_factory import LLMFactory
from mares.memory.agent_memory import AgentMemory
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(abc.ABC):
    """Abstract base agent providing a uniform `run` interface.

    Subclasses implement :meth:`run` and may override :meth:`validate_output`.
    Agents share a :class:`LLMFactory`, an :class:`AgentMemory`, and a
    configurable system prompt.
    """

    name: ClassVar[str] = "base_agent"
    description: ClassVar[str] = "Abstract MARES agent."

    def __init__(
        self,
        llm_factory: LLMFactory | None = None,
        memory: AgentMemory | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.llm_factory = llm_factory or LLMFactory()
        self.memory = memory or AgentMemory(agent_name=self.name)
        self.system_prompt = system_prompt or self.default_system_prompt()
        self.kwargs = kwargs
        logger.debug("agent.initialised", agent=self.name)

    # ----- Hooks subclasses must implement ---------------------------------

    @abc.abstractmethod
    async def run(self, input_data: Any) -> BaseModel:
        """Execute the agent's primary behaviour."""

    # ----- Helpers ---------------------------------------------------------

    def default_system_prompt(self) -> str:
        return (
            f"You are {self.name}, a specialized MARES agent. "
            f"{self.description}"
        )

    def remember(self, role: str, content: str) -> None:
        """Append a message to this agent's local memory."""
        self.memory.add(role=role, content=content)

    def recall(self) -> list[dict[str, str]]:
        """Return this agent's full conversation history."""
        return self.memory.history()

    def validate_output(self, output: BaseModel) -> None:
        """Default validation: ensures the output is a Pydantic model."""
        if not isinstance(output, BaseModel):
            raise TypeError(
                f"{self.name} expected Pydantic output, got {type(output).__name__}"
            )


__all__ = ["BaseAgent"]
