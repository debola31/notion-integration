"""Unit tests for exceptions."""

from __future__ import annotations

import pytest

from notion_cli.exceptions import (
    AuthenticationError,
    NotFoundError,
    NotionCLIError,
    RateLimitError,
    ServerError,
    ValidationError,
    exception_from_response,
)


class TestExceptions:
    """Tests for custom exceptions."""

    def test_base_exception(self) -> None:
        """Test NotionCLIError base class."""
        error = NotionCLIError("Test error", {"key": "value"})

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details == {"key": "value"}
        assert error.exit_code == 1
        assert error.code == "error"

    def test_to_dict(self) -> None:
        """Test exception to_dict method."""
        error = NotionCLIError("Test error", {"key": "value"})
        result = error.to_dict()

        assert result == {
            "error": True,
            "code": "error",
            "message": "Test error",
            "details": {"key": "value"},
        }

    def test_authentication_error(self) -> None:
        """Test AuthenticationError."""
        error = AuthenticationError("Invalid token")

        assert error.exit_code == 2
        assert error.code == "authentication_error"

    def test_rate_limit_error(self) -> None:
        """Test RateLimitError with retry info."""
        error = RateLimitError("Rate limited", retry_after=30, attempts=5)

        assert error.exit_code == 5
        assert error.code == "rate_limited"
        assert error.retry_after == 30
        assert error.attempts == 5
        assert error.details["retry_after"] == 30
        assert error.details["attempts"] == 5


class TestExceptionFromResponse:
    """Tests for exception_from_response function."""

    def test_400_validation_error(self) -> None:
        """Test 400 response creates ValidationError."""
        error = exception_from_response(400, {"message": "Invalid", "code": "invalid"})

        assert isinstance(error, ValidationError)
        assert error.message == "Invalid"

    def test_401_authentication_error(self) -> None:
        """Test 401 response creates AuthenticationError."""
        error = exception_from_response(401, {"message": "Unauthorized"})

        assert isinstance(error, AuthenticationError)

    def test_404_not_found_error(self) -> None:
        """Test 404 response creates NotFoundError."""
        error = exception_from_response(404, {"message": "Not found"})

        assert isinstance(error, NotFoundError)

    def test_429_rate_limit_error(self) -> None:
        """Test 429 response creates RateLimitError."""
        error = exception_from_response(429, {"message": "Too many requests"})

        assert isinstance(error, RateLimitError)

    def test_500_server_error(self) -> None:
        """Test 500 response creates ServerError."""
        error = exception_from_response(500, {"message": "Internal error"})

        assert isinstance(error, ServerError)

    def test_unknown_error(self) -> None:
        """Test unknown status code creates base error."""
        error = exception_from_response(418, {"message": "I'm a teapot"})

        assert isinstance(error, NotionCLIError)
        assert not isinstance(error, (ValidationError, AuthenticationError, NotFoundError))
