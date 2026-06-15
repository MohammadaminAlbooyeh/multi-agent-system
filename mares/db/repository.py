"""Async repository for persisting task runs to PostgreSQL."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker

from mares.db.models import AgentOutputModel, TaskRunModel
from mares.models.agent_output import AgentOutput
from mares.models.final_report import FinalReport
from mares.utils.logger import get_logger

logger = get_logger(__name__)


class TaskRunRepository:
    """Async repository for task run persistence.

    Usage:
        repo = TaskRunRepository("postgresql+asyncpg://user:pass@localhost/db")
        await repo.save_run("abc-123", "my task", report)
    """

    def __init__(self, database_url: str | None = None) -> None:
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._database_url = database_url

    async def _ensure_connected(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is not None:
            return self._session_factory
        if not self._database_url:
            raise RuntimeError("No database_url configured — call set_database_url() first.")
        logger.info("repository.connect", url=self._database_url.split("@")[-1] if "@" in self._database_url else "configured")
        engine = create_async_engine(self._database_url, echo=False)
        self._engine = engine
        self._session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin():
            pass
        sf = self._session_factory
        return sf

    async def save_run(
        self,
        task_id: str,
        description: str,
        report: FinalReport | None = None,
        status: str = "completed",
    ) -> None:
        try:
            sf = await self._ensure_connected()
            async with sf() as session:
                run = TaskRunModel(
                    task_id=task_id,
                    description=description[:500],
                    status=status,
                    report_markdown=report.markdown if report else None,
                    metadata_json=report.metadata if report else None,
                )
                session.add(run)
                await session.commit()
            logger.info("repository.saved_run", task_id=task_id)
        except Exception as exc:
            logger.warning("repository.save_failed", error=str(exc))

    async def save_outputs(
        self,
        task_id: str,
        outputs: list[AgentOutput],
    ) -> None:
        try:
            sf = await self._ensure_connected()
            async with sf() as session:
                for out in outputs:
                    row = AgentOutputModel(
                        task_id=task_id,
                        agent=out.agent,
                        sub_task_id=out.sub_task_id,
                        content=out.content if isinstance(out.content, dict | list) else {"text": str(out.content)},
                        metadata_json=out.metadata,
                    )
                    session.add(row)
                await session.commit()
            logger.info("repository.saved_outputs", task_id=task_id, count=len(outputs))
        except Exception as exc:
            logger.warning("repository.save_outputs_failed", error=str(exc))

    async def get_run(self, task_id: str) -> dict[str, Any] | None:
        sf = await self._ensure_connected()
        async with sf() as session:
            result = await session.execute(
                select(TaskRunModel).where(TaskRunModel.task_id == task_id)
            )
            row = result.scalar_one_or_none()
            if row is None:
                return None
            return {
                "task_id": row.task_id,
                "description": row.description,
                "status": row.status,
                "report_markdown": row.report_markdown,
                "metadata": row.metadata_json,
                "created_at": str(row.created_at),
            }

    async def close(self) -> None:
        engine = self._engine
        if engine is not None:
            await engine.dispose()
            logger.info("repository.disconnected")
