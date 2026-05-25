from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import APIKey

def get_api_key(db: Session, key_value: str) -> APIKey | None:
    return db.execute(select(APIKey).where(APIKey.key == key_value)).scalar_one_or_none()
