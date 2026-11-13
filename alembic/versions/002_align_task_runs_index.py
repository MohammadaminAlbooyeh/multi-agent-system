"""Align task_runs.task_id with the ORM model (unique index).

The initial migration created both a UNIQUE constraint and a non-unique
index on ``task_runs.task_id``. The ORM declares ``unique=True, index=True``,
which maps to a single unique index. This migration reconciles that drift so
``alembic check`` reports a clean schema.

Revision ID: 002
Revises: 001
Create Date: 2026-11-13
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("task_runs_task_id_key", "task_runs", type_="unique")
    op.drop_index("ix_task_runs_task_id", table_name="task_runs")
    op.create_index(
        "ix_task_runs_task_id",
        "task_runs",
        ["task_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_task_runs_task_id", table_name="task_runs")
    op.create_index(
        "ix_task_runs_task_id",
        "task_runs",
        ["task_id"],
        unique=False,
    )
    op.create_unique_constraint("task_runs_task_id_key", "task_runs", ["task_id"])
