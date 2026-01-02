"""Users API operations."""

from __future__ import annotations

from typing import Any

from notion_cli.client.base import NotionClient
from notion_cli.config import Settings


class UsersAPI:
    """API client for Notion Users."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the Users API client."""
        self.client = NotionClient(settings)

    def list(
        self,
        start_cursor: str | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        List all users in the workspace.

        Args:
            start_cursor: Cursor for pagination.
            page_size: Number of results to return.

        Returns:
            List of user objects.
        """
        params: dict[str, Any] = {}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size

        return self.client.get("/users", params=params if params else None)

    def list_all(self) -> list[dict[str, Any]]:
        """
        List all users (handles pagination).

        Returns:
            List of all user objects.
        """
        all_users: list[dict[str, Any]] = []
        start_cursor: str | None = None

        while True:
            response = self.list(start_cursor=start_cursor, page_size=100)
            all_users.extend(response.get("results", []))

            if not response.get("has_more", False):
                break
            start_cursor = response.get("next_cursor")

        return all_users

    def retrieve(self, user_id: str) -> dict[str, Any]:
        """
        Retrieve a user by ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            User object.
        """
        return self.client.get(f"/users/{user_id}")

    def me(self) -> dict[str, Any]:
        """
        Retrieve the bot user associated with the token.

        Returns:
            Bot user object.
        """
        return self.client.get("/users/me")

    def close(self) -> None:
        """Close the API client."""
        self.client.close()
