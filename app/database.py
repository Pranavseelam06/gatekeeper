import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from fastapi import Depends
from typing import Annotated


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment variables")
engine = create_engine(
    DATABASE_URL,
    pool_size=50,
    max_overflow=50,
    pool_timeout=10,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_session():
    with SessionLocal() as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]
Base = declarative_base()

