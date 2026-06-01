import os
from dotenv import load_dotenv
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session
from app.models import APIKey, RequestLog
from app.database import SessionLocal




load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not set in environment variables")
engine = create_engine(TEST_DATABASE_URL)





@pytest.fixture
def db_session():
    connection = engine.connect()

    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    api_key = APIKey(key="test-valid-key", name="proxy test")
    api_key_two = APIKey(key="test-limited-key", name="proxy test two", rate_limit_capacity=2)
    db_session.add(api_key)
    db_session.add(api_key_two)
    db_session.commit()

    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    test_session_factory = sessionmaker(bind=engine)
    app.state.session_factory = test_session_factory
    
    yield TestClient(app)
    app.dependency_overrides.clear()
    app.state.buckets.clear()

    with test_session_factory() as session:
        session.query(RequestLog).delete()
        session.commit()

    # Restore production session factory
    app.state.session_factory = SessionLocal