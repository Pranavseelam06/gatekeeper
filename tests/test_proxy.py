from fastapi.testclient import TestClient
import httpx

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
