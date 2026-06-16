from fastapi import FastAPI, HTTPException, Depends
from .models import APIKey
from .rate_limit_dependency import enforce_rate_limit
import httpx
import time
from fastapi import Request
from app.database import SessionLocal
from app.models import RequestLog
from contextlib import asynccontextmanager
from app.redis_client import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=5.0)
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)
app.state.buckets = {}
app.state.session_factory = SessionLocal

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/proxy")
async def proxy(request: Request, _: APIKey = Depends(enforce_rate_limit)):
    try:
        r = await request.app.state.http_client.get("https://httpbin.org/get")
        return r.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Bad gateway")


@app.middleware("http")
async def log_proxy_requests(request: Request, call_next):
    if request.url.path != "/proxy":
        return await call_next(request)
    start = time.monotonic()
    response = await call_next(request)
    latency_ms = int((time.monotonic() - start) * 1000)
    try:
        with request.app.state.session_factory() as session:
            print(f"[DEBUG] middleware session bound to: {session.bind.url}", flush=True)
            log = RequestLog(
                api_key_value=request.headers.get("X-API-Key", "<missing>"),
                upstream_url="https://httpbin.org/get",
                status_code=response.status_code,
                latency_ms=latency_ms,
            )
            session.add(log)
            session.commit()
            print(f"[DEBUG] middleware committed log id={log.id}", flush=True)
    except Exception as e:
        print(f"[DEBUG] middleware exception: {e}", flush=True)
        pass
    return response