"""Unit tests for rate limiter."""

from __future__ import annotations

import time

import pytest

from notion_cli.client.rate_limiter import RateLimiter


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    def test_initial_burst(self) -> None:
        """Test that initial burst tokens are available."""
        limiter = RateLimiter(requests_per_second=1.0, max_burst=5)

        # Should be able to acquire burst tokens immediately
        for _ in range(5):
            assert limiter.acquire(timeout=0.1)

    def test_rate_limiting(self) -> None:
        """Test that requests are rate limited after burst."""
        limiter = RateLimiter(requests_per_second=10.0, max_burst=1)

        # Consume the burst
        assert limiter.acquire(timeout=0.1)

        # Next acquire should take ~0.1 seconds
        start = time.monotonic()
        assert limiter.acquire(timeout=0.5)
        elapsed = time.monotonic() - start

        assert elapsed >= 0.05  # Should have waited

    def test_timeout_exceeded(self) -> None:
        """Test that acquire returns False when timeout is exceeded."""
        limiter = RateLimiter(requests_per_second=0.1, max_burst=1)

        # Consume the burst
        assert limiter.acquire(timeout=0.1)

        # Next acquire should timeout
        assert not limiter.acquire(timeout=0.05)

    def test_reset(self) -> None:
        """Test that reset restores burst tokens."""
        limiter = RateLimiter(requests_per_second=1.0, max_burst=3)

        # Consume all tokens
        for _ in range(3):
            limiter.acquire(timeout=0.1)

        # Reset
        limiter.reset()

        # Should have all tokens again
        for _ in range(3):
            assert limiter.acquire(timeout=0.1)

    def test_wait_for_retry(self) -> None:
        """Test wait_for_retry resets tokens."""
        limiter = RateLimiter(requests_per_second=1.0, max_burst=3)

        # Consume all tokens
        for _ in range(3):
            limiter.acquire(timeout=0.1)

        # Wait for retry (short wait for testing)
        limiter.wait_for_retry(0)

        # Should have all tokens again
        for _ in range(3):
            assert limiter.acquire(timeout=0.1)
