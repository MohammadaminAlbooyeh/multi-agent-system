"""FinalReport — the user-facing Markdown report."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class FinalReport(BaseModel):
    """The synthesised final report."""

    markdown: str
    sources: list[str] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, str] = Field(default_factory=dict)


__all__ = ["FinalReport"]
