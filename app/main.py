from fastapi import FastAPI, HTTPException, Depends
from .models import APIKey
from .rate_limit_dependency import enforce_rate_limit
import httpx

app = FastAPI()
app.state.buckets = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/proxy")
async def proxy(_: APIKey = Depends(enforce_rate_limit)): 
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get('https://httpbin.org/get')
            return r.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Bad gateway")