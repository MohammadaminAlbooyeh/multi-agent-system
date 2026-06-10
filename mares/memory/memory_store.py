"""Persistent memory store — pluggable backend (in-memory or Redis)."""

from __future__ import annotations

import json
import os
from typing import Any

from mares.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryStore:
    """Key/value store with optional Redis backend.

    Falls back to an in-process dict if Redis is not available or if
    ``MARES_MEMORY_BACKEND=memory``.
    """

    def __init__(self, backend: str | None = None, redis_url: str | None = None) -> None:
        self.backend = (backend or os.getenv("MARES_MEMORY_BACKEND", "memory")).lower()
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self._memory: dict[str, str] = {}
        self._redis = None
        if self.backend == "redis" and self.redis_url:
            try:
                import redis.asyncio as redis_async  # type: ignore

                self._redis = redis_async.from_url(self.redis_url, decode_responses=True)
                logger.info("memory_store.redis_connected", url=self.redis_url)
            except Exception as exc:  # noqa: BLE001
                logger.warning("memory_store.redis_unavailable", error=str(exc))
                self._redis = None

    async def get(self, key: str) -> Any | None:
        raw = await self._raw_get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            return raw

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        raw = json.dumps(value, default=str)
        if self._redis is not None:
            await self._redis.set(key, raw, ex=ttl)
        else:
            self._memory[key] = raw

    async def delete(self, key: str) -> None:
        if self._redis is not None:
            await self._redis.delete(key)
        else:
            self._memory.pop(key, None)

    async def _raw_get(self, key: str) -> str | None:
        if self._redis is not None:
            return await self._redis.get(key)
        return self._memory.get(key)


__all__ = ["MemoryStore"]
