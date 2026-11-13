"""Research Agent — gathers structured findings for a sub-task using tools."""

from __future__ import annotations

import json
import os
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

    def __init__(
        self,
        tool_executor: ToolExecutor | None = None,
        enable_search: bool | None = None,
        search_results: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(system_prompt=RESEARCH_SYSTEM_PROMPT, **kwargs)
        self.tool_executor = tool_executor or ToolExecutor()
        if enable_search is None:
            enable_search = os.getenv("RESEARCH_ENABLE_SEARCH", "true").lower() not in {
                "0",
                "false",
                "no",
                "off",
            }
        self.enable_search = enable_search
        if search_results is None:
            search_results = int(os.getenv("RESEARCH_SEARCH_RESULTS", "5"))
        self.search_results = max(1, search_results)

    async def _search(self, query: str) -> list[dict[str, Any]]:
        """Run a web search, degrading gracefully if the tool fails."""
        if not self.enable_search:
            return []
        try:
            raw = await self.tool_executor.execute(
                "search",
                query=query,
                num_results=self.search_results,
            )
        except Exception as exc:  # noqa: BLE001 - search is best-effort
            logger.warning("research.search_failed", error=str(exc))
            return []
        if not isinstance(raw, list):
            logger.warning("research.search_unexpected_type", type=type(raw).__name__)
            return []
        return [r for r in raw if isinstance(r, dict)]

    async def run(self, input_data: SubTask) -> ResearchFinding:
        """Research a :class:`SubTask` and return a finding."""
        if not isinstance(input_data, SubTask):
            raise ResearchError("ResearchAgent requires a SubTask instance.")

        search_results = await self._search(input_data.task)
        user_msg = f"Sub-task #{input_data.id}: {input_data.task}"
        if search_results:
            user_msg += (
                "\n\nWeb search results (cite the URLs you rely on):\n"
                + json.dumps(search_results, indent=2)
            )
        self.remember("user", user_msg)
        logger.info(
            "research.start",
            sub_task_id=input_data.id,
            search_results=len(search_results),
        )

        raw = await self._generate(
            system=self.system_prompt,
            user=user_msg,
        )
        self.remember("assistant", raw)

        try:
            payload = safe_json_loads(raw)
            sources = [str(s) for s in payload.get("sources", [])]
            for result in search_results:
                url = str(result.get("url", ""))
                if url and url not in sources:
                    sources.append(url)
            finding = ResearchFinding(
                sub_task_id=input_data.id,
                summary=payload.get("summary", ""),
                facts=list(payload.get("facts", [])),
                sources=sources,
            )
        except (ValueError, TypeError) as exc:
            raise ResearchError(f"Research produced invalid JSON: {exc}") from exc

        self.validate_output(finding)
        logger.info("research.done", sub_task_id=input_data.id, facts=len(finding.facts))
        return finding


__all__ = ["ResearchAgent", "RESEARCH_SYSTEM_PROMPT"]
