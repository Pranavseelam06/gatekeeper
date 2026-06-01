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
    rate_limit_capacity: Mapped[int] = mapped_column(server_default="10", nullable=False)
    rate_limit_refill_rate: Mapped[float] = mapped_column(server_default="1.0", nullable=False)
    def __repr__(self):
        return f"<APIKey(id={self.id}, key='{self.key}', name='{self.name}', created_at='{self.created_at}')>"

class RequestLog(Base):
    __tablename__ = "request_logs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    api_key_value: Mapped[str] = mapped_column(nullable=False, index=True)
    upstream_url: Mapped[str] = mapped_column(nullable=False)
    status_code: Mapped[int] = mapped_column(nullable=False, index=True)
    latency_ms: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    def __repr__(self):
        return f"<RequestLog(id={self.id}, api_key_value={self.api_key_value}, upstream_url={self.upstream_url}, status_code={self.status_code}, latency_ms={self.latency_ms}, created_at='{self.created_at}')>"
    