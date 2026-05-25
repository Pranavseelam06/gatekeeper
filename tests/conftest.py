import os
from dotenv import load_dotenv
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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