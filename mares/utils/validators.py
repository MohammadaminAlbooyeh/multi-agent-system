"""Input validation helpers."""

from __future__ import annotations

from typing import Any

from mares.models.sub_task import SubTask
from mares.utils.exceptions import PlanningError, ValidationError


def validate_non_empty_string(value: Any, name: str = "value") -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name!r} must be a non-empty string.")
    return value.strip()


def validate_task_graph(sub_tasks: list[SubTask]) -> None:
    """Validate a list of sub-tasks forms a valid DAG (no cycles, no dup IDs)."""
    seen: set[int] = set()
    for st in sub_tasks:
        if st.id in seen:
            raise PlanningError(f"Duplicate sub-task id: {st.id}")
        seen.add(st.id)
        for dep in st.depends_on:
            if dep == st.id:
                raise PlanningError(f"Sub-task {st.id} depends on itself.")
            if dep not in seen and dep not in {s.id for s in sub_tasks}:
                # Defer the "unknown dep" check until after the first pass.
                if dep not in {s.id for s in sub_tasks}:
                    raise PlanningError(
                        f"Sub-task {st.id} depends on unknown id {dep}."
                    )

    # Cycle check.
    state: dict[int, int] = {st.id: 0 for st in sub_tasks}  # 0=unseen, 1=visiting, 2=done
    graph: dict[int, list[int]] = {st.id: list(st.depends_on) for st in sub_tasks}

    def dfs(u: int) -> None:
        if state[u] == 1:
            raise PlanningError("Cycle detected in sub-task graph.")
        if state[u] == 2:
            return
        state[u] = 1
        for v in graph[u]:
            dfs(v)
        state[u] = 2

    for st in sub_tasks:
        if state[st.id] == 0:
            dfs(st.id)


__all__ = ["validate_non_empty_string", "validate_task_graph", "ValidationError"]
