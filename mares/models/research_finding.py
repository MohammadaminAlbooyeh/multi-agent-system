"""ResearchFinding — structured output of the Research Agent."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ResearchFinding(BaseModel):
    """A research result tied to a specific sub-task."""

    sub_task_id: int
    summary: str = ""
    facts: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


__all__ = ["ResearchFinding"]
