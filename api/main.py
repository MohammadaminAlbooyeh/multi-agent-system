"""FastAPI entry point for the MARES API."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from api.websocket_handler import websocket_endpoint
from mares.communication.event_bus import EventBus
from mares.orchestrator.orchestrator import Orchestrator
from mares.utils.config import get_settings
from mares.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Spin up shared resources on startup, tear them down on shutdown."""
    settings = get_settings()
    app.state.settings = settings
    app.state.event_bus = EventBus()
    app.state.orchestrator = Orchestrator()
    app.state.tasks: dict[str, asyncio.Task] = {}
    logger.info("api.startup", host=settings.api_host, port=settings.api_port)
    try:
        yield
    finally:
        for t in app.state.tasks.values():
            t.cancel()
        logger.info("api.shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="MARES — Multi-Agent Research & Execution System",
        version="0.1.0",
        description="A production-grade multi-agent orchestration API.",
        lifespan=lifespan,
    )

    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1")
    app.add_api_websocket_route("/ws/tasks/{task_id}", websocket_endpoint)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.api_log_level,
        reload=True,
    )


__all__ = ["app", "create_app"]
