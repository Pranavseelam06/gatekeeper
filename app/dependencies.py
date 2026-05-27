from sqlalchemy.orm import Session
from fastapi import Depends, Header, HTTPException
from .models import APIKey
from .crud import get_api_key
from .database import get_session

def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key"), 
                    db: Session = Depends(get_session)) -> APIKey:
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    api_key = get_api_key(db, x_api_key)
    if api_key is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return api_key
