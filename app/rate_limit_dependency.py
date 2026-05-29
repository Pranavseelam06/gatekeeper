from fastapi import Depends, HTTPException, Request
from app.dependencies import require_api_key
from app.models import APIKey
from app.rate_limiter import TokenBucket

RATE_LIMIT_CAPACITY = 10
RATE_LIMIT_REFILL_RATE = 1.0

def enforce_rate_limit(
    request: Request,
    api_key: APIKey = Depends(require_api_key),
) -> APIKey:
    buckets = request.app.state.buckets
    if api_key.key not in buckets:
        buckets[api_key.key] = TokenBucket(
            capacity=RATE_LIMIT_CAPACITY, 
            refill_rate=RATE_LIMIT_REFILL_RATE
        )
    bucket = buckets[api_key.key]
    if not bucket.consume():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return api_key
        