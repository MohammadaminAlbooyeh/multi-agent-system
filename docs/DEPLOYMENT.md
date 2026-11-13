# Deployment

## Local

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in keys
uvicorn api.main:app --reload
```

## Docker

```bash
cp .env.example .env   # fill in LLM keys at minimum
docker compose up --build
```

This starts three services:

- `api` — the FastAPI app (port 8000). The image entrypoint runs
  `alembic upgrade head` before starting Uvicorn, so the schema is created
  automatically on first boot.
- `postgres` — persistent state.
- `redis` — shared memory + message queue (enable with
  `MARES_MEMORY_BACKEND=redis`).

If ports `5432`/`6379` are already used on the host, run with a compose
override that removes the Postgres/Redis host mappings — the API reaches
them over the compose network regardless.

## Production checklist

- [ ] Set strong `POSTGRES_PASSWORD` and `REDIS_URL`.
- [ ] Restrict `CORS_ORIGINS` to your actual frontend.
- [ ] Put the API behind a TLS-terminating reverse proxy.
- [ ] Mount persistent volumes for Postgres data.
- [ ] Add Prometheus + Grafana for monitoring (suggested: cAdvisor + node-exporter).
- [ ] Set `TOKEN_BUDGET_GLOBAL` to a sensible cap.
- [ ] Enable `TOOL_FAILURE_RATE=0.0` in production (use it only in tests).
