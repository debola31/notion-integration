"""Unit tests for cache."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from notion_cli.client.cache import Cache


class TestCache:
    """Tests for the Cache class."""

    def test_get_set(self, tmp_path: Path) -> None:
        """Test basic get and set operations."""
        cache = Cache(cache_dir=tmp_path, default_ttl=60)

        try:
            cache.set("/test", None, {"foo": "bar"})
            result = cache.get("/test", None)

            assert result == {"foo": "bar"}
        finally:
            cache.close()

    def test_get_missing(self, tmp_path: Path) -> None:
        """Test get returns None for missing keys."""
        cache = Cache(cache_dir=tmp_path, default_ttl=60)

        try:
            result = cache.get("/nonexistent", None)
            assert result is None
        finally:
            cache.close()

    def test_cache_with_params(self, tmp_path: Path) -> None:
        """Test caching with different params."""
        cache = Cache(cache_dir=tmp_path, default_ttl=60)

        try:
            cache.set("/test", {"page": 1}, {"data": "page1"})
            cache.set("/test", {"page": 2}, {"data": "page2"})

            assert cache.get("/test", {"page": 1}) == {"data": "page1"}
            assert cache.get("/test", {"page": 2}) == {"data": "page2"}
        finally:
            cache.close()

    def test_cache_disabled(self, tmp_path: Path) -> None:
        """Test cache when disabled."""
        cache = Cache(cache_dir=tmp_path, default_ttl=60, enabled=False)

        try:
            cache.set("/test", None, {"foo": "bar"})
            result = cache.get("/test", None)

            assert result is None
        finally:
            cache.close()

    def test_invalidate(self, tmp_path: Path) -> None:
        """Test cache invalidation."""
        cache = Cache(cache_dir=tmp_path, default_ttl=60)

        try:
            cache.set("/test1", None, {"foo": "bar"})
            cache.set("/test2", None, {"baz": "qux"})

            count = cache.invalidate()

            assert count == 2
            assert cache.get("/test1", None) is None
            assert cache.get("/test2", None) is None
        finally:
            cache.close()

    def test_context_manager(self, tmp_path: Path) -> None:
        """Test cache as context manager."""
        with Cache(cache_dir=tmp_path, default_ttl=60) as cache:
            cache.set("/test", None, {"foo": "bar"})
            result = cache.get("/test", None)
            assert result == {"foo": "bar"}
