"""HTTP routes for the MARES API."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from api.schemas import (
    PlanRequest,
    PlanResponse,
    RunRequest,
    RunResponse,
    StatusResponse,
    TaskGraph,
)
from mares.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/plan", response_model=PlanResponse, summary="Decompose a task into a DAG")
async def plan(request: PlanRequest, req: Request) -> PlanResponse:
    """Run only the Planner Agent and return the resulting task graph."""
    orchestrator = req.app.state.orchestrator
    try:
        plan_obj = await orchestrator.plan_only(request.task)
    except Exception as exc:  # noqa: BLE001
        logger.error("api.plan.failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Planning failed: {exc}") from exc

    return PlanResponse(
        task=plan_obj.description,
        sub_tasks=[
            TaskGraph(
                id=st.id,
                task=st.task,
                depends_on=st.depends_on,
            )
            for st in plan_obj.sub_tasks
        ],
    )


@router.post("/run", response_model=RunResponse, summary="Run a task end-to-end")
async def run(request: RunRequest, background: BackgroundTasks, req: Request) -> RunResponse:
    """Kick off a full MARES run. Returns immediately with a ``task_id``."""
    orchestrator = req.app.state.orchestrator
    event_bus = req.app.state.event_bus
    task_id = str(uuid.uuid4())

    async def _runner() -> None:
        try:
            report = await orchestrator.run(request.task)
            await event_bus.emit(
                "task.completed",
                task_id=task_id,
                report=report.model_dump(),
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("api.run.failed", task_id=task_id, error=str(exc))
            await event_bus.emit("task.failed", task_id=task_id, error=str(exc))

    req.app.state.tasks[task_id] = asyncio.create_task(_runner())
    return RunResponse(task_id=task_id, status="started", task=request.task)


@router.get("/status/{task_id}", response_model=StatusResponse, summary="Get run status")
async def status(task_id: str, req: Request) -> StatusResponse:
    task: asyncio.Task | None = req.app.state.tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Unknown task_id")
    if task.done():
        if task.exception():
            return StatusResponse(task_id=task_id, status="failed", error=str(task.exception()))
        return StatusResponse(task_id=task_id, status="completed")
    return StatusResponse(task_id=task_id, status="running")


@router.get("/agents", summary="List available agents")
async def list_agents() -> dict[str, list[dict[str, Any]]]:
    return {
        "agents": [
            {"name": "planner_agent", "role": "Decompose + DAG"},
            {"name": "research_agent", "role": "Web/file research"},
            {"name": "execution_agent", "role": "Code generation + run"},
            {"name": "critic_agent", "role": "Validation + retry"},
            {"name": "synthesizer_agent", "role": "Final report"},
        ]
    }


@router.get("/tools", summary="List registered tools")
async def list_tools(req: Request) -> dict[str, list[dict[str, Any]]]:
    from mares.tools.tool_registry import default_registry

    return {"tools": default_registry.describe()}


__all__ = ["router"]
