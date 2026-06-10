# DAG Execution

MARES represents the task plan as a **Directed Acyclic Graph** of
`SubTask` nodes. The graph is built by the Planner, validated, and then
executed in topological waves.

## Data model

`mares.graph.dag.DAG` is a minimal in-memory graph with:

- `add_node(id, data=None)` — register a node.
- `add_edge(src, dst)` — add a `src → dst` edge; raises on cycle.
- `topological_sort()` — Kahn's algorithm.
- `levels()` — group nodes by "execution wave" (longest-path level).
- `_has_cycle()` — DFS-based cycle detection.

## Example

Planner output:

```json
{
  "tasks": [
    {"id": 1, "task": "Research Celery", "depends_on": []},
    {"id": 2, "task": "Search failures", "depends_on": []},
    {"id": 3, "task": "Analyse logs", "depends_on": [1, 2]},
    {"id": 4, "task": "Prototype fix", "depends_on": [3]},
    {"id": 5, "task": "Final report", "depends_on": [3, 4]}
  ]
}
```

Execution waves:

```
Level 0: [1, 2]      # run in parallel
Level 1: [3]         # waits for 1 + 2
Level 2: [4]         # waits for 3
Level 3: [5]         # waits for 3 + 4
```

## `DAGExecutor`

`mares.orchestrator.dag_executor.DAGExecutor` ties the planner output,
DAG primitives, and `ParallelRunner` together. For each wave, it dispatches
every sub-task to the appropriate agent and collects the `AgentOutput`s.
