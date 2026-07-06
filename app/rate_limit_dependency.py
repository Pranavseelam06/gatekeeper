from fastapi import Depends, HTTPException, Request
from app.dependencies import require_api_key
from app.models import APIKey
from app.rate_limiter import TokenBucket

def enforce_rate_limit(
    request: Request,
    api_key: APIKey = Depends(require_api_key),
) -> APIKey:
    buckets = request.app.state.buckets

    bucket_key = f"api_key:{api_key.id}"

    with request.app.state.buckets_lock:
        if bucket_key not in buckets:
            buckets[bucket_key] = TokenBucket(
                capacity=api_key.rate_limit_capacity,
                refill_rate=api_key.rate_limit_refill_rate,
            )
        bucket = buckets[bucket_key]

    if not bucket.consume():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    return api_key