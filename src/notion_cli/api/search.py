"""Search API operations."""

from __future__ import annotations

from typing import Any, Literal

from notion_cli.client.base import NotionClient
from notion_cli.config import Settings


class SearchAPI:
    """API client for Notion Search."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the Search API client."""
        self.client = NotionClient(settings)

    def search(
        self,
        query: str | None = None,
        filter_type: Literal["page", "database"] | None = None,
        sort_direction: Literal["ascending", "descending"] | None = None,
        sort_timestamp: Literal["last_edited_time"] | None = None,
        start_cursor: str | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        Search for pages and databases.

        Args:
            query: Search query string.
            filter_type: Filter by object type ("page" or "database").
            sort_direction: Sort direction.
            sort_timestamp: Sort by timestamp field.
            start_cursor: Cursor for pagination.
            page_size: Number of results to return.

        Returns:
            Search results.
        """
        payload: dict[str, Any] = {}

        if query:
            payload["query"] = query
        if filter_type:
            payload["filter"] = {"value": filter_type, "property": "object"}
        if sort_direction and sort_timestamp:
            payload["sort"] = {
                "direction": sort_direction,
                "timestamp": sort_timestamp,
            }
        if start_cursor:
            payload["start_cursor"] = start_cursor
        if page_size:
            payload["page_size"] = page_size

        return self.client.post("/search", json_data=payload if payload else None)

    def search_all(
        self,
        query: str | None = None,
        filter_type: Literal["page", "database"] | None = None,
        sort_direction: Literal["ascending", "descending"] | None = None,
        sort_timestamp: Literal["last_edited_time"] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search and return all results (handles pagination).

        Args:
            query: Search query string.
            filter_type: Filter by object type.
            sort_direction: Sort direction.
            sort_timestamp: Sort by timestamp field.

        Returns:
            List of all matching objects.
        """
        all_results: list[dict[str, Any]] = []
        start_cursor: str | None = None

        while True:
            response = self.search(
                query=query,
                filter_type=filter_type,
                sort_direction=sort_direction,
                sort_timestamp=sort_timestamp,
                start_cursor=start_cursor,
                page_size=100,
            )
            all_results.extend(response.get("results", []))

            if not response.get("has_more", False):
                break
            start_cursor = response.get("next_cursor")

        return all_results

    def close(self) -> None:
        """Close the API client."""
        self.client.close()
