"""Research Agent — gathers structured findings for a sub-task using tools."""

from __future__ import annotations

from typing import Any, ClassVar

from mares.agents.base_agent import BaseAgent
from mares.models.research_finding import ResearchFinding
from mares.models.sub_task import SubTask
from mares.tools.tool_executor import ToolExecutor
from mares.utils.exceptions import ResearchError
from mares.utils.json_utils import safe_json_loads
from mares.utils.logger import get_logger

logger = get_logger(__name__)


RESEARCH_SYSTEM_PROMPT = """You are the MARES Research Agent.
You receive a single sub-task and produce a structured JSON finding:
{
  "summary": "one-paragraph synthesis",
  "facts": ["bullet 1", "bullet 2", ...],
  "sources": ["url1", "url2", ...]
}

You have access to tools (search, file, api). Use them when helpful.
Return ONLY JSON.
"""


class ResearchAgent(BaseAgent):
    """Runs per sub-task and produces a :class:`ResearchFinding`."""

    name: ClassVar[str] = "research_agent"
    description: ClassVar[str] = (
        "Researches a sub-task using tools and returns structured findings."
    )

    def __init__(self, tool_executor: ToolExecutor | None = None, **kwargs: Any) -> None:
        super().__init__(system_prompt=RESEARCH_SYSTEM_PROMPT, **kwargs)
        self.tool_executor = tool_executor or ToolExecutor()

    async def run(self, input_data: SubTask) -> ResearchFinding:
        """Research a :class:`SubTask` and return a finding."""
        if not isinstance(input_data, SubTask):
            raise ResearchError("ResearchAgent requires a SubTask instance.")

        user_msg = f"Sub-task #{input_data.id}: {input_data.task}"
        self.remember("user", user_msg)
        logger.info("research.start", sub_task_id=input_data.id)

        raw = await self.llm_factory.generate(
            system=self.system_prompt,
            user=user_msg,
        )
        self.remember("assistant", raw)

        try:
            payload = safe_json_loads(raw)
            finding = ResearchFinding(
                sub_task_id=input_data.id,
                summary=payload.get("summary", ""),
                facts=list(payload.get("facts", [])),
                sources=list(payload.get("sources", [])),
            )
        except (ValueError, TypeError) as exc:
            raise ResearchError(f"Research produced invalid JSON: {exc}") from exc

        self.validate_output(finding)
        logger.info("research.done", sub_task_id=input_data.id, facts=len(finding.facts))
        return finding


__all__ = ["ResearchAgent", "RESEARCH_SYSTEM_PROMPT"]
