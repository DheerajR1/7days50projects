# Distributed Queue-Based Load Balancer System

Ugh. One door in. Many workers. Queue decide who chew next job.

## Architecture

```text
Client -> FastAPI API Gateway -> Redis Queue (RQ) -> Worker Pool
                      |                     |
                      v                     v
                 PostgreSQL <--------- Worker Heartbeats
                      |
                      v
               Web Dashboard (vanilla HTML/JS/CSS)
```

## Features
- `POST /submit` queues job and returns immediately.
- `GET /status/{job_id}` checks job state.
- `GET /workers` returns worker health/load from Redis registry.
- `GET /metrics-summary` returns system stats for dashboard.
- Prometheus metrics at `/metrics`.
- Redis-backed FIFO queue with RQ.
- Retry with exponential backoff (up to 3).
- Idempotency-Key support.
- IP rate limiting (429).
- Docker Compose deployment.

## Run

```bash
docker compose up --build
```

API: http://localhost:8000
Dashboard: http://localhost:5173

## Config (env)
- `REDIS_URL`
- `POSTGRES_URL`
- `QUEUE_NAME`
- `RATE_LIMIT`
- `WORKER_ID`
- `WORKER_IP`
- `MAX_CAPACITY`

## Endpoints
### POST /submit
```json
{ "payload": { "duration": 2, "data": "abc" } }
```
Response:
```json
{ "job_id": "uuid", "status": "queued" }
```

### GET /status/{job_id}
```json
{ "job_id": "...", "status": "running", "worker": "worker-1", "result": null }
```

## Notes
- Pull-based worker model only (no direct routing to worker IPs).
- Worker marked down when heartbeat stale.
- Dead queue behavior can be extended by adding a dedicated failed queue consumer.
- Optional enhancements planned: priority queues + websocket stream (SSE/WS) for push updates.

## Code Review (self-check)
- Verified queue-only distribution and no worker direct assignment in API.
- Confirmed idempotency key dedupes submit path.
- Confirmed status lifecycle persisted in PostgreSQL.
- Confirmed heartbeat registry + stale detection for worker DOWN state.
- Confirmed dashboard polls for near-real-time metrics.
