"""SQLAlchemy ORM models for MARES persistence."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TaskRunModel(Base):
    __tablename__ = "task_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(64), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(String(32), default="running")
    report_markdown = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class AgentOutputModel(Base):
    __tablename__ = "agent_outputs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(64), nullable=False, index=True)
    agent = Column(String(64), nullable=False)
    sub_task_id = Column(Integer, nullable=False)
    content = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


__all__ = ["Base", "TaskRunModel", "AgentOutputModel"]
