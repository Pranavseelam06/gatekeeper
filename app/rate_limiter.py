import time

class TokenBucket:
     #Token bucket rate limiter. Bucket starts full; tokens refill at refill_rate per second up to capacity.
    tokens: float
    capacity: int
    last_refill: float
    refill_rate: float

    def __init__(self, capacity: int, refill_rate: float):
        self.tokens = capacity
        self.capacity = capacity
        self.last_refill = time.monotonic()
        self.refill_rate = refill_rate

    def consume(self) -> bool:
        #Try to consume one token. Returns True if allowed, False if bucket is empty (rate limited).
        now = time.monotonic()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        else:
            return False
        




