from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from app.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    def __repr__(self):
        return f"<APIKey(id={self.id}, key='{self.key}', name='{self.name}', created_at='{self.created_at}')>"

    