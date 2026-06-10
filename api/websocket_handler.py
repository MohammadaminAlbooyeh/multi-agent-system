"""WebSocket handler for streaming real-time task updates."""

from __future__ import annotations

import asyncio

from fastapi import WebSocket, WebSocketDisconnect

from mares.utils.logger import get_logger

logger = get_logger(__name__)


async def websocket_endpoint(websocket: WebSocket, task_id: str) -> None:
    """Stream events for a running task to a connected client.

    The client subscribes by opening ``/ws/tasks/{task_id}``. The server
    pushes JSON messages as the orchestrator emits them on the event bus.
    """
    await websocket.accept()
    bus = websocket.app.state.event_bus
    queue: asyncio.Queue = asyncio.Queue(maxsize=256)

    async def listener(event: dict) -> None:
        await queue.put(event)

    bus.on("task.completed", listener)
    bus.on("task.failed", listener)
    bus.on("task.progress", listener)

    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
            except asyncio.TimeoutError:
                # Heartbeat so the client knows the connection is alive.
                await websocket.send_json({"type": "ping"})
                continue
            await websocket.send_json({"type": "event", "task_id": task_id, **event})
    except WebSocketDisconnect:
        logger.info("websocket.disconnected", task_id=task_id)
    finally:
        bus.off("task.completed", listener)
        bus.off("task.failed", listener)
        bus.off("task.progress", listener)


__all__ = ["websocket_endpoint"]
