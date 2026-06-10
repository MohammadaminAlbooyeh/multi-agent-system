"""FastAPI dependency injection helpers."""

from __future__ import annotations

from fastapi import Request

from mares.orchestrator.orchestrator import Orchestrator
from mares.communication.event_bus import EventBus


def get_orchestrator(request: Request) -> Orchestrator:
    return request.app.state.orchestrator


def get_event_bus(request: Request) -> EventBus:
    return request.app.state.event_bus


__all__ = ["get_orchestrator", "get_event_bus"]
