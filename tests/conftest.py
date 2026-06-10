"""Shared pytest fixtures and configuration."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Make the project root importable when running ``pytest`` from any cwd.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Ensure no real API keys are required during tests.
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("GROQ_API_KEY", "test-key")


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_task_string() -> str:
    return "Analyze why Celery tasks fail intermittently in distributed systems."


@pytest.fixture
def sample_sub_tasks():
    from mares.models.sub_task import SubTask

    return [
        SubTask(id=1, task="Research Celery architecture", depends_on=[]),
        SubTask(id=2, task="Search for known failure modes", depends_on=[]),
        SubTask(id=3, task="Analyze distributed system logs", depends_on=[1, 2]),
        SubTask(id=4, task="Write fix prototype code", depends_on=[3]),
        SubTask(id=5, task="Synthesize final report", depends_on=[3, 4]),
    ]
