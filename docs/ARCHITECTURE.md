# MARES Architecture

```
                        ┌──────────────────────┐
                        │       User Task      │
                        └──────────┬───────────┘
                                   │
                          ┌────────▼─────────┐
                          │ Planner Agent    │  Decompose → SubTask list
                          │  + DAG Builder   │  Build adjacency graph
                          └────────┬─────────┘
                                   │
                          ┌────────▼─────────┐
                          │   DAG Executor   │  Topological sort → waves
                          │  + Parallel Run  │  Independent tasks in parallel
                          └────────┬─────────┘
                                   │
                       ┌───────────┴───────────┐
                       │                       │
                  Research Agent         Execution Agent
                  (uses tools)           (Python sandbox)
                       │                       │
                       └───────────┬───────────┘
                                   │
                          ┌────────▼─────────┐
                          │  Critic Agent    │  Validate / hallucination
                          └────────┬─────────┘
                                   │ pass/fail
                          ┌────────▼─────────┐
                          │ Self-Correction  │  Retry up to N times
                          └────────┬─────────┘
                                   │
                          ┌────────▼─────────┐
                          │  Synthesizer     │  Markdown final report
                          └────────┬─────────┘
                                   │
                          ┌────────▼─────────┐
                          │   Final Report   │
                          └──────────────────┘
```

## Module layout

- `mares/agents/` — all five specialized agents.
- `mares/orchestrator/` — DAG execution, parallel runner, self-correction.
- `mares/tools/` — tool registry, executor, and built-in tools.
- `mares/memory/` — agent + shared memory + persistent store.
- `mares/graph/` — DAG primitives.
- `mares/llm/` — multi-provider LLM factory + cost controller.
- `mares/communication/` — message queue + event bus.
- `mares/evaluation/` — evaluator, hallucination, consistency checkers.
- `mares/models/` — Pydantic data models.
- `mares/utils/` — config, logger, retry, timeout, validation.
- `api/` — FastAPI app (HTTP + WebSocket).
- `tests/` — unit + integration test suites.
