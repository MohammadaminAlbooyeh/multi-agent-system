"""Unit tests for the DAG, TaskNode, and DependencyResolver."""

from __future__ import annotations

import pytest

from mares.graph.dag import DAG
from mares.graph.dependency_resolver import DependencyResolver
from mares.utils.exceptions import PlanningError


def test_dag_add_nodes_and_edges():
    dag = DAG()
    dag.add_node(1)
    dag.add_node(2)
    dag.add_edge(1, 2)
    assert dag.node_count() == 2
    assert dag.edge_count() == 1
    assert dag.children(1) == [2]
    assert dag.parents(2) == [1]


def test_dag_detects_cycle():
    dag = DAG()
    for n in (1, 2, 3):
        dag.add_node(n)
    dag.add_edge(1, 2)
    dag.add_edge(2, 3)
    with pytest.raises(PlanningError):
        dag.add_edge(3, 1)


def test_dag_rejects_self_loop():
    dag = DAG()
    dag.add_node(1)
    with pytest.raises(ValueError):
        dag.add_edge(1, 1)


def test_dag_topological_sort():
    dag = DAG()
    for n in (1, 2, 3, 4):
        dag.add_node(n)
    dag.add_edge(1, 3)
    dag.add_edge(2, 3)
    dag.add_edge(3, 4)
    order = dag.topological_sort()
    assert order.index(3) > order.index(1)
    assert order.index(3) > order.index(2)
    assert order.index(4) > order.index(3)


def test_dag_levels():
    dag = DAG()
    for n in (1, 2, 3, 4, 5):
        dag.add_node(n)
    dag.add_edge(1, 3)
    dag.add_edge(2, 3)
    dag.add_edge(3, 4)
    dag.add_edge(4, 5)
    levels = dag.levels()
    assert sorted(levels[0]) == [1, 2]
    assert levels[1] == [3]
    assert levels[2] == [4]
    assert levels[3] == [5]


def test_dependency_resolver_returns_waves():
    dag = DAG()
    for n, deps in {1: [], 2: [], 3: [1, 2], 4: [3]}.items():
        dag.add_node(n, data=f"task-{n}")
        for d in deps:
            dag.add_edge(d, n)

    resolver = DependencyResolver(dag)
    waves = resolver.execution_waves()
    assert [len(w) for w in waves] == [2, 1, 1]
