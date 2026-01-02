"""Disk-based caching for Notion API responses.

Uses diskcache for persistent caching across CLI invocations.
Only caches GET requests (read operations).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from diskcache import Cache as DiskCache


class Cache:
    """Disk-based cache for API responses."""

    def __init__(
        self,
        cache_dir: Path | None = None,
        default_ttl: int = 300,  # 5 minutes
        enabled: bool = True,
    ) -> None:
        """
        Initialize the cache.

        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.cache/notion-cli
            default_ttl: Default time-to-live in seconds.
            enabled: Whether caching is enabled.
        """
        self.enabled = enabled
        self.default_ttl = default_ttl

        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "notion-cli"

        self.cache_dir = cache_dir
        self._cache: DiskCache | None = None

    @property
    def cache(self) -> DiskCache:
        """Lazily initialize the disk cache."""
        if self._cache is None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._cache = DiskCache(str(self.cache_dir))
        return self._cache

    def _make_key(self, endpoint: str, params: dict[str, Any] | None = None) -> str:
        """Generate a cache key from endpoint and params."""
        key_data = {"endpoint": endpoint, "params": params or {}}
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """
        Get a cached response.

        Args:
            endpoint: API endpoint path.
            params: Query parameters used in the request.

        Returns:
            Cached response data or None if not found/expired.
        """
        if not self.enabled:
            return None

        key = self._make_key(endpoint, params)
        value = self.cache.get(key)

        if value is not None:
            return json.loads(value)  # type: ignore[no-any-return]
        return None

    def set(
        self,
        endpoint: str,
        params: dict[str, Any] | None,
        value: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """
        Cache a response.

        Args:
            endpoint: API endpoint path.
            params: Query parameters used in the request.
            value: Response data to cache.
            ttl: Time-to-live in seconds. Uses default if not specified.
        """
        if not self.enabled:
            return

        key = self._make_key(endpoint, params)
        expire = ttl if ttl is not None else self.default_ttl
        self.cache.set(key, json.dumps(value), expire=expire)

    def invalidate(self, pattern: str | None = None) -> int:
        """
        Invalidate cache entries.

        Args:
            pattern: Optional pattern to match (not currently implemented,
                     clears all entries).

        Returns:
            Number of entries removed.
        """
        if not self.enabled:
            return 0

        # For simplicity, clear all entries
        # Pattern matching could be added later if needed
        count = len(self.cache)
        self.cache.clear()
        return count

    def close(self) -> None:
        """Close the cache connection."""
        if self._cache is not None:
            self._cache.close()
            self._cache = None

    def __enter__(self) -> "Cache":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
