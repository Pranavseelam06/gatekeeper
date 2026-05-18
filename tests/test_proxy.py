from fastapi.testclient import TestClient
from app.main import app
import httpx

client = TestClient(app)

def test_proxy_success(respx_mock):
    respx_mock.get("https://httpbin.org/get").mock(return_value=httpx.Response(200, json={"message": "ok", "data": [1, 2, 3]}))
    response = client.get("/proxy")
    assert response.status_code == 200
    assert response.json() == {"message": "ok", "data": [1, 2, 3]}

def test_proxy_upstream_failure(respx_mock):
    respx_mock.get("https://httpbin.org/get").mock(side_effect=httpx.RequestError("Something went wrong"))
    response = client.get("/proxy")
    assert response.status_code == 502
    assert response.json() == {"detail": "Bad gateway"}


