# Gatekeeper

[![CI](https://github.com/Pranavseelam06/gatekeeper/actions/workflows/ci.yml/badge.svg)](https://github.com/Pranavseelam06/gatekeeper/actions/workflows/ci.yml)

A production-style API gateway in Python/FastAPI with API key authentication, per-key rate limiting, and structured request logging.

## Features

- **API key authentication** — `X-API-Key` header validated against database; returns 401 for missing or invalid keys
- **Per-key rate limiting** — token bucket algorithm with configurable capacity and refill rate stored per API key in the database
- **Async proxy** — forwards authenticated requests to upstream services with explicit timeout handling (502 for connection errors, 504 for timeouts)
- **Structured request logging** — every `/proxy` request recorded to a `request_logs` table for observability and auditing
- **Versioned schema** — Alembic migrations with separate routing for production and test databases

## Stack

Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL 16, pytest

## Endpoints

- `GET /health` — liveness check
- `GET /proxy` — authenticated, rate-limited, logged proxy to upstream (currently `https://httpbin.org/get`)

## Local development

```bash