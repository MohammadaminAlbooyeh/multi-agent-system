# Deployment

## Local

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in keys
uvicorn api.main:app --reload
```

## Docker

```bash
docker compose up --build
```

This starts three services:

- `api` — the FastAPI app (port 8000).
- `postgres` — persistent state.
- `redis` — shared memory + message queue.

## Production checklist

- [ ] Set strong `POSTGRES_PASSWORD` and `REDIS_URL`.
- [ ] Restrict `CORS_ORIGINS` to your actual frontend.
- [ ] Put the API behind a TLS-terminating reverse proxy.
- [ ] Mount persistent volumes for Postgres data.
- [ ] Add Prometheus + Grafana for monitoring (suggested: cAdvisor + node-exporter).
- [ ] Set `TOKEN_BUDGET_GLOBAL` to a sensible cap.
- [ ] Enable `TOOL_FAILURE_RATE=0.0` in production (use it only in tests).
