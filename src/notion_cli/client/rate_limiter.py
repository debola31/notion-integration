"""Rate limiting for Notion API requests.

Implements a token bucket algorithm to respect Notion's rate limits:
- Average 3 requests per second per integration
- Respects Retry-After header on 429 responses
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field


@dataclass
class RateLimiter:
    """Token bucket rate limiter for API requests."""

    requests_per_second: float = 3.0
    max_burst: int = 5
    tokens: float = field(init=False)
    last_refill: float = field(init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def __post_init__(self) -> None:
        """Initialize token count and timestamp."""
        self.tokens = float(self.max_burst)
        self.last_refill = time.monotonic()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.requests_per_second
        self.tokens = min(self.max_burst, self.tokens + new_tokens)
        self.last_refill = now

    def acquire(self, timeout: float | None = None) -> bool:
        """
        Acquire a token, blocking until one is available.

        Args:
            timeout: Maximum time to wait for a token. None means wait forever.

        Returns:
            True if token acquired, False if timeout expired.
        """
        start_time = time.monotonic()

        with self._lock:
            while True:
                self._refill()

                if self.tokens >= 1:
                    self.tokens -= 1
                    return True

                # Calculate wait time until we have a token
                wait_time = (1 - self.tokens) / self.requests_per_second

                if timeout is not None:
                    elapsed = time.monotonic() - start_time
                    remaining = timeout - elapsed
                    if remaining <= 0:
                        return False
                    wait_time = min(wait_time, remaining)

                # Release lock while waiting
                self._lock.release()
                try:
                    time.sleep(wait_time)
                finally:
                    self._lock.acquire()

    def wait_for_retry(self, retry_after: int) -> None:
        """
        Wait for the specified retry-after period.

        Called when a 429 response is received with a Retry-After header.

        Args:
            retry_after: Number of seconds to wait before retrying.
        """
        time.sleep(retry_after)
        # Reset tokens after waiting for rate limit reset
        with self._lock:
            self.tokens = float(self.max_burst)
            self.last_refill = time.monotonic()

    def reset(self) -> None:
        """Reset the rate limiter to initial state."""
        with self._lock:
            self.tokens = float(self.max_burst)
            self.last_refill = time.monotonic()
