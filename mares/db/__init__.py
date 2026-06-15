"""Database models and repository for MARES persistence."""

from __future__ import annotations

from mares.db.models import Base
from mares.db.repository import TaskRunRepository

__all__ = ["Base", "TaskRunRepository"]
