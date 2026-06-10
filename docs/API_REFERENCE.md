# API Reference

All HTTP endpoints live under the `/api/v1` prefix.

## `POST /api/v1/plan`

Run only the Planner Agent. Returns the task graph.

```http
POST /api/v1/plan
Content-Type: application/json

{"task": "Investigate X"}
```

Response:

```json
{
  "task": "Investigate X",
  "sub_tasks": [
    {"id": 1, "task": "...", "depends_on": []}
  ]
}
```

## `POST /api/v1/run`

Kick off a full MARES run. Returns immediately with a `task_id`.

```http
POST /api/v1/run
Content-Type: application/json

{"task": "Investigate X and write code"}
```

Response:

```json
{"task_id": "...", "status": "started", "task": "..."}
```

## `GET /api/v1/status/{task_id}`

Get the status of a running or completed task.

## `GET /api/v1/agents`

List available agents.

## `GET /api/v1/tools`

List registered tools.

## `WS /ws/tasks/{task_id}`

Stream real-time events for a running task. Receives:

```json
{"type": "ping"}
{"type": "event", "task_id": "...", "event": "task.completed", ...}
```
