from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import APIKey
from app.redis_client import redis_client, get_cached_api_key, cache_api_key


def get_api_key(db: Session, key_value: str):
    cached_key = get_cached_api_key(redis_client, key_value)

    if cached_key is not None:
        return cached_key

    api_key = db.execute(
        select(APIKey).where(APIKey.key == key_value)
    ).scalar_one_or_none()

    if api_key is None:
        return None

    cache_api_key(redis_client, key_value, api_key)

    return api_key