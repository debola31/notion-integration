"""Configuration management for Notion CLI."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

OutputFormat = Literal["json", "pretty", "compact", "markdown"]


@dataclass
class Settings:
    """Application settings loaded from environment variables and CLI options."""

    token: str | None = None
    output_format: OutputFormat = "json"
    use_cache: bool = True
    cache_ttl: int = 300  # 5 minutes
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".cache" / "notion-cli")
    debug: bool = False
    timeout: float = 30.0
    max_retries: int = 5
    requests_per_second: float = 3.0

    def __post_init__(self) -> None:
        """Load token from environment if not provided."""
        if self.token is None:
            self.token = os.environ.get("NOTION_INTEGRATION_TOKEN")

    @property
    def has_token(self) -> bool:
        """Check if a valid token is configured."""
        return self.token is not None and len(self.token) > 0

    def get_token(self) -> str:
        """Get the token, raising an error if not configured."""
        if not self.has_token:
            from notion_cli.exceptions import AuthenticationError

            raise AuthenticationError(
                "No Notion token configured. "
                "Set NOTION_INTEGRATION_TOKEN environment variable or use --token option."
            )
        return self.token  # type: ignore[return-value]


# Global default settings instance
_default_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _default_settings
    if _default_settings is None:
        _default_settings = Settings()
    return _default_settings


def set_settings(settings: Settings) -> None:
    """Set the global settings instance."""
    global _default_settings
    _default_settings = settings
