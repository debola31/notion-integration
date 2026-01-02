"""Pytest configuration and fixtures."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Generator
from unittest.mock import patch

import pytest

from notion_cli.client.cache import Cache
from notion_cli.client.rate_limiter import RateLimiter
from notion_cli.config import Settings


@pytest.fixture
def test_token() -> str:
    """Provide a test token."""
    return "secret_test_token_123"


@pytest.fixture
def settings(test_token: str, tmp_path: Path) -> Settings:
    """Provide test settings."""
    return Settings(
        token=test_token,
        output_format="json",
        use_cache=True,
        cache_dir=tmp_path / "cache",
        debug=False,
    )


@pytest.fixture
def settings_no_cache(test_token: str, tmp_path: Path) -> Settings:
    """Provide test settings with cache disabled."""
    return Settings(
        token=test_token,
        output_format="json",
        use_cache=False,
        cache_dir=tmp_path / "cache",
        debug=False,
    )


@pytest.fixture
def rate_limiter() -> RateLimiter:
    """Provide a rate limiter for testing."""
    return RateLimiter(requests_per_second=10.0, max_burst=10)


@pytest.fixture
def cache(tmp_path: Path) -> Generator[Cache, None, None]:
    """Provide a cache instance for testing."""
    cache_instance = Cache(cache_dir=tmp_path / "cache", default_ttl=60)
    yield cache_instance
    cache_instance.close()


@pytest.fixture
def mock_env_token(test_token: str) -> Generator[None, None, None]:
    """Mock the NOTION_INTEGRATION_TOKEN environment variable."""
    with patch.dict(os.environ, {"NOTION_INTEGRATION_TOKEN": test_token}):
        yield


@pytest.fixture
def sample_page_response() -> dict[str, Any]:
    """Provide a sample page response."""
    return {
        "object": "page",
        "id": "page-123",
        "created_time": "2024-01-01T00:00:00.000Z",
        "last_edited_time": "2024-01-02T00:00:00.000Z",
        "parent": {"type": "workspace", "workspace": True},
        "properties": {
            "title": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": "Test Page"}}],
            }
        },
        "archived": False,
    }


@pytest.fixture
def sample_database_response() -> dict[str, Any]:
    """Provide a sample database response."""
    return {
        "object": "database",
        "id": "db-123",
        "created_time": "2024-01-01T00:00:00.000Z",
        "last_edited_time": "2024-01-02T00:00:00.000Z",
        "title": [{"type": "text", "text": {"content": "Test Database"}}],
        "properties": {
            "Name": {"id": "title", "type": "title", "title": {}},
            "Status": {
                "id": "status",
                "type": "select",
                "select": {
                    "options": [
                        {"id": "1", "name": "Todo", "color": "red"},
                        {"id": "2", "name": "Done", "color": "green"},
                    ]
                },
            },
        },
        "archived": False,
    }


@pytest.fixture
def sample_block_response() -> dict[str, Any]:
    """Provide a sample block response."""
    return {
        "object": "block",
        "id": "block-123",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": "Hello, world!"}}]
        },
        "has_children": False,
        "archived": False,
    }


@pytest.fixture
def sample_user_response() -> dict[str, Any]:
    """Provide a sample user response."""
    return {
        "object": "user",
        "id": "user-123",
        "type": "person",
        "name": "Test User",
        "avatar_url": None,
        "person": {"email": "test@example.com"},
    }


@pytest.fixture
def sample_search_response(sample_page_response: dict[str, Any]) -> dict[str, Any]:
    """Provide a sample search response."""
    return {
        "object": "list",
        "results": [sample_page_response],
        "has_more": False,
        "next_cursor": None,
    }
