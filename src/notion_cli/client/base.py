"""Base HTTP client for Notion API.

Handles authentication, rate limiting, caching, and retries.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import (
    RetryError,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from notion_cli.client.cache import Cache
from notion_cli.client.rate_limiter import RateLimiter
from notion_cli.config import Settings
from notion_cli.exceptions import (
    NetworkError,
    NotionCLIError,
    RateLimitError,
    ServerError,
    exception_from_response,
)

logger = logging.getLogger(__name__)


class NotionClient:
    """HTTP client for Notion API with rate limiting, caching, and retries."""

    BASE_URL = "https://api.notion.com/v1"
    API_VERSION = "2022-06-28"

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the Notion client.

        Args:
            settings: Application settings containing token and configuration.
        """
        self.settings = settings
        self.token = settings.get_token()

        self.rate_limiter = RateLimiter(
            requests_per_second=settings.requests_per_second
        )

        self.cache = Cache(
            cache_dir=settings.cache_dir,
            default_ttl=settings.cache_ttl,
            enabled=settings.use_cache,
        )

        self._client = httpx.Client(
            base_url=self.BASE_URL,
            timeout=settings.timeout,
            headers=self._default_headers(),
        )

    def _default_headers(self) -> dict[str, str]:
        """Get default headers for all requests."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.API_VERSION,
            "Content-Type": "application/json",
        }

    def _should_retry(self, exc: Exception) -> bool:
        """Determine if the request should be retried."""
        if isinstance(exc, RateLimitError):
            return True
        if isinstance(exc, ServerError):
            return True
        if isinstance(exc, NetworkError):
            return True
        return False

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a single HTTP request (internal, used by retry logic)."""
        # Acquire rate limit token
        self.rate_limiter.acquire()

        try:
            response = self._client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
            )
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out: {e}") from e
        except httpx.ConnectError as e:
            raise NetworkError(f"Connection failed: {e}") from e
        except httpx.HTTPError as e:
            raise NetworkError(f"HTTP error: {e}") from e

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "1"))
            self.rate_limiter.wait_for_retry(retry_after)
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=retry_after,
            )

        # Handle errors
        if response.status_code >= 400:
            try:
                body = response.json()
            except Exception:
                body = {"message": response.text}
            raise exception_from_response(response.status_code, body)

        return response.json()  # type: ignore[no-any-return]

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        use_cache: bool | None = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP request with retries, rate limiting, and caching.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE).
            endpoint: API endpoint path (e.g., "/pages/abc123").
            params: Query parameters.
            json_data: JSON body for POST/PATCH requests.
            use_cache: Override cache setting for this request.

        Returns:
            Parsed JSON response.
        """
        # Check cache for GET requests
        should_cache = (use_cache if use_cache is not None else self.settings.use_cache)
        if method == "GET" and should_cache:
            cached = self.cache.get(endpoint, params)
            if cached is not None:
                logger.debug(f"Cache hit for {endpoint}")
                return cached

        # Create retry-wrapped request function
        @retry(
            stop=stop_after_attempt(self.settings.max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=60),
            retry=retry_if_exception_type((RateLimitError, ServerError, NetworkError)),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )
        def request_with_retry() -> dict[str, Any]:
            return self._make_request(method, endpoint, params, json_data)

        try:
            result = request_with_retry()
        except RetryError as e:
            # Re-raise the last exception from retries
            if e.last_attempt.exception() is not None:
                raise e.last_attempt.exception() from e
            raise

        # Cache successful GET responses
        if method == "GET" and should_cache:
            self.cache.set(endpoint, params, result)

        return result

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        use_cache: bool | None = None,
    ) -> dict[str, Any]:
        """Make a GET request."""
        return self.request("GET", endpoint, params=params, use_cache=use_cache)

    def post(
        self,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return self.request("POST", endpoint, params=params, json_data=json_data)

    def patch(
        self,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a PATCH request."""
        return self.request("PATCH", endpoint, params=params, json_data=json_data)

    def delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint, params=params)

    def close(self) -> None:
        """Close the HTTP client and cache."""
        self._client.close()
        self.cache.close()

    def __enter__(self) -> "NotionClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
