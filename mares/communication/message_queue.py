"""In-process async message queue — mini-Kafka for agent messaging."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator

from mares.communication.message import Message
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class MessageQueue:
    """Topic-based pub/sub with per-recipient queues.

    Producers :meth:`publish` messages; consumers :meth:`subscribe` to a
    topic and iterate with ``async for``. Each subscriber gets its own
    bounded queue so a slow consumer can't block others.
    """

    def __init__(self, max_queue_size: int = 1024) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[Message]]] = defaultdict(list)
        self._max = max_queue_size
        self._lock = asyncio.Lock()

    async def publish(self, message: Message) -> None:
        topic = message.topic or "_default"
        async with self._lock:
            queues = list(self._subscribers.get(topic, []))
        logger.debug("message_queue.publish", topic=topic, queues=len(queues))
        for q in queues:
            if q.full():
                # Drop oldest to make room.
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            await q.put(message)

    async def subscribe(self, topic: str) -> AsyncIterator[Message]:
        queue: asyncio.Queue[Message] = asyncio.Queue(maxsize=self._max)
        async with self._lock:
            self._subscribers[topic].append(queue)
        try:
            while True:
                msg = await queue.get()
                yield msg
        finally:
            async with self._lock:
                self._subscribers[topic].remove(queue)

    async def size(self, topic: str) -> int:
        async with self._lock:
            return len(self._subscribers.get(topic, []))


__all__ = ["MessageQueue"]
