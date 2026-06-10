# Self-Correction Loop

The `SelfCorrectionLoop` (`mares.orchestrator.self_correction_loop`)
wraps the `DAGExecutor` and re-runs only the failing sub-tasks when the
Critic rejects an output.

## Algorithm

1. Run all sub-tasks.
2. Pass outputs to the Critic.
3. If `report.passed == True` → done.
4. Else, collect `report.failed_subtask_ids()` and re-run **only** those.
5. Repeat up to `max_retries` times.

## Configuring retries

```python
from mares.orchestrator.self_correction_loop import SelfCorrectionLoop

loop = SelfCorrectionLoop(dag_executor=executor, critic=critic, max_retries=5)
```

## Why per-sub-task retries?

Re-running the whole DAG is wasteful when 9/10 sub-tasks were fine. The
loop surgically replaces the rejected outputs and merges the new ones
back in by `sub_task_id`.
