"""Custom exceptions for Notion CLI."""

from __future__ import annotations

from typing import Any


class NotionCLIError(Exception):
    """Base exception for all CLI errors."""

    exit_code: int = 1
    code: str = "error"

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for JSON output."""
        result: dict[str, Any] = {
            "error": True,
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


class AuthenticationError(NotionCLIError):
    """Token missing or invalid."""

    exit_code = 2
    code = "authentication_error"


class NotFoundError(NotionCLIError):
    """Resource not found (404)."""

    exit_code = 3
    code = "not_found"


class ValidationError(NotionCLIError):
    """Invalid request parameters (400)."""

    exit_code = 4
    code = "validation_error"


class RateLimitError(NotionCLIError):
    """Rate limited (429) - after retries exhausted."""

    exit_code = 5
    code = "rate_limited"

    def __init__(
        self, message: str, retry_after: int | None = None, attempts: int = 0
    ) -> None:
        details = {"retry_after": retry_after, "attempts": attempts}
        super().__init__(message, details)
        self.retry_after = retry_after
        self.attempts = attempts


class PermissionError(NotionCLIError):
    """Access denied (403)."""

    exit_code = 6
    code = "permission_denied"


class ServerError(NotionCLIError):
    """Notion API server error (5xx)."""

    exit_code = 7
    code = "server_error"


class NetworkError(NotionCLIError):
    """Connection or timeout error."""

    exit_code = 8
    code = "network_error"


class ConflictError(NotionCLIError):
    """Conflict error (409)."""

    exit_code = 9
    code = "conflict"


def exception_from_response(status_code: int, body: dict[str, Any]) -> NotionCLIError:
    """Create appropriate exception from Notion API error response."""
    message = body.get("message", "Unknown error")
    code = body.get("code", "unknown")

    error_map: dict[int, type[NotionCLIError]] = {
        400: ValidationError,
        401: AuthenticationError,
        403: PermissionError,
        404: NotFoundError,
        409: ConflictError,
        429: RateLimitError,
    }

    if status_code in error_map:
        exception_class = error_map[status_code]
        if exception_class == RateLimitError:
            return RateLimitError(message)
        return exception_class(message, {"notion_code": code})

    if status_code >= 500:
        return ServerError(message, {"status_code": status_code, "notion_code": code})

    return NotionCLIError(message, {"status_code": status_code, "notion_code": code})
