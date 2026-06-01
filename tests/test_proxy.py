from fastapi.testclient import TestClient
from app.models import RequestLog
import httpx
from sqlalchemy import text

def test_proxy_success(respx_mock, client: TestClient):
    respx_mock.get("https://httpbin.org/get").mock(return_value=httpx.Response(200, json={"message": "ok", "data": [1, 2, 3]}))
    response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
    assert response.status_code == 200
    assert response.json() == {"message": "ok", "data": [1, 2, 3]}

def test_proxy_upstream_failure(respx_mock, client: TestClient):
    respx_mock.get("https://httpbin.org/get").mock(side_effect=httpx.RequestError("Something went wrong"))
    response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
    assert response.status_code == 502
    assert response.json() == {"detail": "Bad gateway"}

def test_proxy_timeout_failure(respx_mock, client: TestClient):
    respx_mock.get("https://httpbin.org/get").mock(side_effect=httpx.TimeoutException("Something went wrong"))
    response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
    assert response.status_code == 504
    assert response.json() == {"detail": "Gateway timeout"}

def test_proxy_missing_api_key_returns_401(client):
    response = client.get("/proxy")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

def test_proxy_invalid_api_key_returns_401(client):
    response = client.get("/proxy", headers={"X-API-Key": "test-invalid-key"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

def test_proxy_rate_limit_returns_429_when_exhausted(client, respx_mock, monkeypatch):
    monkeypatch.setattr("app.rate_limiter.time.monotonic", lambda: 0)
    respx_mock.get("https://httpbin.org/get").mock(return_value=httpx.Response(200, json={"ok": True}))
    for _ in range (10):
        response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
        assert response.status_code == 200
        assert response.json() == {"ok": True}
    response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded"}

def test_proxy_rate_limit_recovers_after_refill(client, respx_mock, monkeypatch):
    monkeypatch.setattr("app.rate_limiter.time.monotonic", lambda: 0)
    respx_mock.get("https://httpbin.org/get").mock(return_value=httpx.Response(200, json={"ok": True}))
    for _ in range (10):
        response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
        assert response.status_code == 200
        assert response.json() == {"ok": True}
    monkeypatch.setattr("app.rate_limiter.time.monotonic", lambda: 1)
    response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded"}
    
def test_proxy_rate_limit_differs_per_api_key(client, respx_mock, monkeypatch):
    monkeypatch.setattr("app.rate_limiter.time.monotonic", lambda: 0)
    respx_mock.get("https://httpbin.org/get").mock(return_value=httpx.Response(200, json={"ok": True}))
    for _ in range (10):
        response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
        assert response.status_code == 200
        assert response.json() == {"ok": True}
    response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded"}
    for _ in range (2):
        response = client.get("/proxy", headers={"X-API-Key": "test-limited-key"})
        assert response.status_code == 200
        assert response.json() == {"ok": True}
    response = client.get("/proxy", headers={"X-API-Key": "test-limited-key"})
    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded"}

def test_proxy_logs_requests(client, respx_mock, db_session):
    respx_mock.get("https://httpbin.org/get").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )

    response = client.get(
        "/proxy",
        headers={"X-API-Key": "test-valid-key"}
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True}

    log_entry = (
        db_session.query(RequestLog)
        .order_by(RequestLog.id.desc())
        .first()
    )

    assert log_entry is not None
    assert log_entry.api_key_value == "test-valid-key"
    assert log_entry.upstream_url == "https://httpbin.org/get"
    assert log_entry.status_code == 200
    assert isinstance(log_entry.latency_ms, int)

def test_proxy_logs_unauthorized_requests(client, respx_mock, db_session):
    response = client.get("/proxy")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

    log_entry = (
        db_session.query(RequestLog)
        .order_by(RequestLog.id.desc())
        .first()
    )

    assert log_entry is not None
    assert log_entry.api_key_value == "<missing>"
    assert log_entry.upstream_url == "https://httpbin.org/get"
    assert log_entry.status_code == 401
    assert isinstance(log_entry.latency_ms, int)

def test_proxy_logs_rate_limited_requests(client, respx_mock, db_session, monkeypatch):
    monkeypatch.setattr("app.rate_limiter.time.monotonic", lambda: 0)
    respx_mock.get("https://httpbin.org/get").mock(return_value=httpx.Response(200, json={"ok": True}))
    for _ in range (10):
        response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
        assert response.status_code == 200
        assert response.json() == {"ok": True}
    response = client.get("/proxy", headers={"X-API-Key": "test-valid-key"})
    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded"}

    log_entry = (
        db_session.query(RequestLog)
        .order_by(RequestLog.id.desc())
        .first()
    )

    assert log_entry is not None
    assert log_entry.api_key_value == "test-valid-key"
    assert log_entry.upstream_url == "https://httpbin.org/get"
    assert log_entry.status_code == 429
    assert isinstance(log_entry.latency_ms, int)