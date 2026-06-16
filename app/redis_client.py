import hashlib
import json
import os
from types import SimpleNamespace

import redis
from dotenv import load_dotenv


load_dotenv()

redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)


def api_key_cache_key(raw_api_key: str) -> str:
    hashed = hashlib.sha256(raw_api_key.encode()).hexdigest()
    return f"api_key:{hashed}"


def cache_api_key(redis_client, key_value: str, api_key) -> None:
    cache_key = api_key_cache_key(key_value)

    data = {
        "id": api_key.id,
        "name": api_key.name,
        "rate_limit_capacity": api_key.rate_limit_capacity,
        "rate_limit_refill_rate": api_key.rate_limit_refill_rate,
    }

    redis_client.setex(
        cache_key,
        300,
        json.dumps(data),
    )


def get_cached_api_key(redis_client, key_value: str):
    cache_key = api_key_cache_key(key_value)

    cached = redis_client.get(cache_key)

    if cached is None:
        return None

    data = json.loads(cached)

    return SimpleNamespace(**data)