"""Directed Acyclic Graph — minimal in-memory implementation."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Hashable, Iterator

from mares.utils.exceptions import PlanningError


class DAG:
    """Adjacency-list based DAG with cycle detection + topological sort."""

    def __init__(self) -> None:
        self._nodes: dict[Hashable, Any] = {}
        self._edges: dict[Hashable, list[Hashable]] = defaultdict(list)
        # Reverse index: child -> set(parents)  (preserves duplicates? we store as list)
        self._parents: dict[Hashable, list[Hashable]] = defaultdict(list)

    # ----- mutators ----------------------------------------------------------

    def add_node(self, node_id: Hashable, data: Any = None) -> None:
        if node_id in self._nodes:
            raise ValueError(f"Node {node_id!r} already exists.")
        self._nodes[node_id] = data
        self._edges.setdefault(node_id, [])
        self._parents.setdefault(node_id, [])

    def add_edge(self, src: Hashable, dst: Hashable) -> None:
        if src not in self._nodes or dst not in self._nodes:
            raise KeyError(f"Unknown node(s): src={src!r}, dst={dst!r}")
        if src == dst:
            raise ValueError("Self-loops are not allowed in a DAG.")
        self._edges[src].append(dst)
        self._parents[dst].append(src)
        if self._has_cycle():
            # Roll back the edge.
            self._edges[src].pop()
            self._parents[dst].pop()
            raise PlanningError(f"Adding edge {src!r}->{dst!r} would create a cycle.")

    # ----- queries -----------------------------------------------------------

    def nodes(self) -> list[Hashable]:
        return list(self._nodes.keys())

    def node_count(self) -> int:
        return len(self._nodes)

    def edge_count(self) -> int:
        return sum(len(v) for v in self._edges.values())

    def children(self, node_id: Hashable) -> list[Hashable]:
        return list(self._edges.get(node_id, []))

    def parents(self, node_id: Hashable) -> list[Hashable]:
        return list(self._parents.get(node_id, []))

    def get(self, node_id: Hashable) -> Any:
        return self._nodes[node_id]

    def __contains__(self, node_id: Hashable) -> bool:
        return node_id in self._nodes

    def __iter__(self) -> Iterator[Hashable]:
        return iter(self._nodes)

    # ----- algorithms --------------------------------------------------------

    def _has_cycle(self) -> bool:
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[Hashable, int] = {n: WHITE for n in self._nodes}

        def dfs(u: Hashable) -> bool:
            color[u] = GRAY
            for v in self._edges.get(u, []):
                if color[v] == GRAY:
                    return True
                if color[v] == WHITE and dfs(v):
                    return True
            color[u] = BLACK
            return False

        return any(color[n] == WHITE and dfs(n) for n in self._nodes)

    def topological_sort(self) -> list[Hashable]:
        """Kahn's algorithm — returns a valid topological ordering."""
        if not self._nodes:
            return []
        in_degree: dict[Hashable, int] = {n: len(self._parents[n]) for n in self._nodes}
        queue: deque[Hashable] = deque(n for n, d in in_degree.items() if d == 0)
        order: list[Hashable] = []
        while queue:
            u = queue.popleft()
            order.append(u)
            for v in self._edges[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        if len(order) != len(self._nodes):
            raise PlanningError("Cycle detected — topological sort impossible.")
        return order

    def levels(self) -> list[list[Hashable]]:
        """Group nodes by topological "wave" (longest-path level)."""
        in_degree = {n: len(self._parents[n]) for n in self._nodes}
        level_of: dict[Hashable, int] = {n: 0 for n in self._nodes}
        queue: deque[Hashable] = deque(n for n, d in in_degree.items() if d == 0)
        visited = 0
        max_level = 0
        while queue:
            u = queue.popleft()
            visited += 1
            max_level = max(max_level, level_of[u])
            for v in self._edges[u]:
                level_of[v] = max(level_of[v], level_of[u] + 1)
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if visited != len(self._nodes):
            raise PlanningError("Cycle detected — cannot compute levels.")

        waves: list[list[Hashable]] = [[] for _ in range(max_level + 1)]
        for n, lvl in level_of.items():
            waves[lvl].append(n)
        return waves


__all__ = ["DAG"]
