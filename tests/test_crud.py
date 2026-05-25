from app.models import APIKey
from app.crud import get_api_key

def test_get_api_key_returns_row_when_key_exists(db_session):
    api_key = APIKey(key="testkey", name="Test Key")
    db_session.add(api_key)
    db_session.commit()

    key_received = get_api_key(db_session, "testkey")
    assert key_received is not None
    assert key_received.key == "testkey"

def test_get_api_key_returns_none_when_key_missing(db_session):
    key_received = get_api_key(db_session, "missingkey")
    assert key_received is None


    