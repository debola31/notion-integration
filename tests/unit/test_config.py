"""Unit tests for configuration."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from notion_cli.config import Settings, get_settings, set_settings
from notion_cli.exceptions import AuthenticationError


class TestSettings:
    """Tests for the Settings class."""

    def test_default_settings(self) -> None:
        """Test default settings values."""
        settings = Settings(token="test_token")

        assert settings.token == "test_token"
        assert settings.output_format == "json"
        assert settings.use_cache is True
        assert settings.debug is False
        assert settings.timeout == 30.0
        assert settings.max_retries == 5

    def test_token_from_env(self) -> None:
        """Test token is loaded from environment variable."""
        with patch.dict(os.environ, {"NOTION_INTEGRATION_TOKEN": "env_token"}):
            settings = Settings()
            assert settings.token == "env_token"

    def test_has_token(self) -> None:
        """Test has_token property."""
        settings_with_token = Settings(token="test")
        assert settings_with_token.has_token is True

        settings_without_token = Settings(token=None)
        with patch.dict(os.environ, {}, clear=True):
            # Clear any existing token
            settings_without_token.token = None
            assert settings_without_token.has_token is False

    def test_get_token_raises_without_token(self) -> None:
        """Test get_token raises AuthenticationError when no token."""
        settings = Settings(token=None)
        settings.token = None  # Ensure no token

        with pytest.raises(AuthenticationError):
            settings.get_token()

    def test_get_token_returns_token(self) -> None:
        """Test get_token returns the token when available."""
        settings = Settings(token="my_token")
        assert settings.get_token() == "my_token"

    def test_custom_cache_dir(self, tmp_path: Path) -> None:
        """Test custom cache directory."""
        settings = Settings(token="test", cache_dir=tmp_path / "custom")
        assert settings.cache_dir == tmp_path / "custom"


class TestGlobalSettings:
    """Tests for global settings management."""

    def test_get_set_settings(self) -> None:
        """Test getting and setting global settings."""
        original = Settings(token="original")
        set_settings(original)

        assert get_settings().token == "original"

        new = Settings(token="new")
        set_settings(new)

        assert get_settings().token == "new"
