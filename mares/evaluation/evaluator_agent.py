"""Evaluator Agent — score an agent's output 0-100."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, Field

from mares.agents.base_agent import BaseAgent
from mares.llm.llm_factory import LLMFactory
from mares.utils.json_utils import safe_json_loads
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class QualityScore(BaseModel):
    agent: str
    score: int = Field(ge=0, le=100)
    accuracy: int = Field(ge=0, le=100)
    completeness: int = Field(ge=0, le=100)
    notes: str = ""


class EvaluatorAgent(BaseAgent):
    """LLM-as-judge that produces a structured :class:`QualityScore`."""

    name: ClassVar[str] = "evaluator_agent"
    description: ClassVar[str] = "Scores another agent's output from 0 to 100."

    SYSTEM_PROMPT = """You are the MARES Evaluator. Score the supplied agent
output on accuracy and completeness from 0-100 and return JSON:
{
  "score": 0-100,
  "accuracy": 0-100,
  "completeness": 0-100,
  "notes": "short rationale"
}
Return ONLY JSON.
"""

    def __init__(self, llm_factory: LLMFactory | None = None, **kwargs: Any) -> None:
        super().__init__(system_prompt=self.SYSTEM_PROMPT, llm_factory=llm_factory, **kwargs)

    async def run(self, input_data: dict[str, Any]) -> QualityScore:
        agent_name = input_data.get("agent", "unknown")
        content = input_data.get("content", "")
        raw = await self.llm_factory.generate(
            system=self.system_prompt,
            user=str(content),
        )
        payload = safe_json_loads(raw)
        return QualityScore(
            agent=agent_name,
            score=int(payload.get("score", 0)),
            accuracy=int(payload.get("accuracy", 0)),
            completeness=int(payload.get("completeness", 0)),
            notes=str(payload.get("notes", "")),
        )


__all__ = ["EvaluatorAgent", "QualityScore"]
