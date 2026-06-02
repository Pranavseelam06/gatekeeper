````md
# Gatekeeper

[![CI](https://github.com/Pranavseelam06/gatekeeper/actions/workflows/ci.yml/badge.svg)](https://github.com/Pranavseelam06/gatekeeper/actions/workflows/ci.yml)

A production-style API gateway in Python/FastAPI with API key authentication, per-key rate limiting, and structured request logging.

**Live URL:** https://gatekeeper-ccgq.onrender.com/docs

## Features

- **API Key Authentication** — Validates incoming requests via the `X-API-Key` header against a cloud-hosted datastore; handles invalid credentials with immediate `401 Unauthorized` responses.
- **Per-Key Token-Bucket Rate Limiting** — Enforces traffic limits using an asynchronous token-bucket algorithm configured through database parameters (`rate_limit_capacity`, `rate_limit_refill_rate`).
- **Resilient Async Proxy** — Forwards authenticated traffic to upstream services with timeout protection and proper error handling.
- **Structured Request Logging** — Captures request metadata including route, status code, latency, and client IP for observability and auditing.
- **Environment Isolation** — Supports Local, CI, and Production environments through environment-variable based configuration.

## Architecture & Stack

- **Framework:** Python 3.12, FastAPI, Uvicorn
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Database:** Neon PostgreSQL
- **Deployment:** Docker, Render
- **Testing:** Pytest, GitHub Actions

## Endpoints

| Method | Endpoint | Description |
|----------|----------|-------------|
| GET | `/` | Health check |
| GET | `/docs` | Swagger UI documentation |
| GET | `/proxy` | Authenticated, rate-limited proxy endpoint |

---

## Infrastructure Deployment

```text
[ Local Client / curl ] --- (HTTPS) ---> [ Render Container ]
                                                |
                                         (Auth & Logging)
                                                v
                                     [ Neon PostgreSQL ]
````

### Production Configuration

* `DATABASE_URL` — PostgreSQL connection string
* `PORT` — Container port (default: `8000`)

---

## Local Development

### 1. Configure Environment Variables

Create a `.env` file:

```env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/gatekeeper"
TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/gatekeeper_test"
```

### 2. Start PostgreSQL

```bash
docker-compose up -d
```

### 3. Apply Migrations

```bash
alembic upgrade head
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Run Tests

```bash
pytest
```

```
```
