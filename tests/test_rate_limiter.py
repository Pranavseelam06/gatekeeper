from app.rate_limiter import TokenBucket
import time
import pytest

def test_fresh_bucket_allows_capacity_requests_immediately(monkeypatch):
    monkeypatch.setattr(time, "monotonic", lambda: 0)
    bucket = TokenBucket(capacity=10, refill_rate=1.0)
    for _ in range(10):
        var = bucket.consume()
        assert var

def test_bucket_denies_after_capacity_exhausted(monkeypatch):
    monkeypatch.setattr(time, "monotonic", lambda: 0)
    bucket = TokenBucket(capacity=10, refill_rate=1.0)
    for _ in range(10):
        var = bucket.consume()
        assert var
    var = bucket.consume()
    assert var is False
    

def test_bucket_refills_at_correct_rate(monkeypatch):
    monkeypatch.setattr(time, "monotonic", lambda: 0)
    bucket = TokenBucket(capacity=10, refill_rate=2.0)
    for _ in range(10):
        bucket.consume()
    monkeypatch.setattr(time, "monotonic", lambda: 1)
    for _ in range(2):
        var = bucket.consume()
        assert var
    var = bucket.consume()
    assert var is False

def test_bucket_caps_at_capacity_even_after_long_idle(monkeypatch):
    monkeypatch.setattr(time, "monotonic", lambda: 0)
    bucket = TokenBucket(capacity=10, refill_rate=1.0)
    for _ in range(10):
        bucket.consume()
    monkeypatch.setattr(time, "monotonic", lambda: 10000)
    for _ in range(10):
        var = bucket.consume()
        assert var
    var = bucket.consume()
    assert var is False
    