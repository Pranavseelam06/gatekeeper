from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/proxy")
async def proxy():
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get('https://httpbin.org/get')
            return r.json()
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Bad gateway")