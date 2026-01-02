"""Databases API operations."""

from __future__ import annotations

from typing import Any

from notion_cli.client.base import NotionClient
from notion_cli.config import Settings


class DatabasesAPI:
    """API client for Notion Databases."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the Databases API client."""
        self.client = NotionClient(settings)

    def retrieve(self, database_id: str) -> dict[str, Any]:
        """
        Retrieve a database by ID.

        Args:
            database_id: The ID of the database to retrieve.

        Returns:
            Database object.
        """
        return self.client.get(f"/databases/{database_id}")

    def query(
        self,
        database_id: str,
        filter_obj: dict[str, Any] | None = None,
        sorts: list[dict[str, Any]] | None = None,
        start_cursor: str | None = None,
        page_size: int | None = None,
        filter_properties: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Query a database.

        Args:
            database_id: The ID of the database to query.
            filter_obj: Filter conditions.
            sorts: Sort conditions.
            start_cursor: Cursor for pagination.
            page_size: Number of results to return (max 100).
            filter_properties: Properties to include in results.

        Returns:
            Query results with list of pages.
        """
        payload: dict[str, Any] = {}
        if filter_obj:
            payload["filter"] = filter_obj
        if sorts:
            payload["sorts"] = sorts
        if start_cursor:
            payload["start_cursor"] = start_cursor
        if page_size:
            payload["page_size"] = page_size
        if filter_properties:
            payload["filter_properties"] = filter_properties

        return self.client.post(
            f"/databases/{database_id}/query",
            json_data=payload if payload else None,
        )

    def query_all(
        self,
        database_id: str,
        filter_obj: dict[str, Any] | None = None,
        sorts: list[dict[str, Any]] | None = None,
        filter_properties: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query all pages from a database (handles pagination).

        Args:
            database_id: The ID of the database to query.
            filter_obj: Filter conditions.
            sorts: Sort conditions.
            filter_properties: Properties to include in results.

        Returns:
            List of all matching pages.
        """
        all_results: list[dict[str, Any]] = []
        start_cursor: str | None = None

        while True:
            response = self.query(
                database_id,
                filter_obj=filter_obj,
                sorts=sorts,
                start_cursor=start_cursor,
                page_size=100,
                filter_properties=filter_properties,
            )
            all_results.extend(response.get("results", []))

            if not response.get("has_more", False):
                break
            start_cursor = response.get("next_cursor")

        return all_results

    def create(
        self,
        parent: dict[str, Any],
        title: list[dict[str, Any]],
        properties: dict[str, Any],
        icon: dict[str, Any] | None = None,
        cover: dict[str, Any] | None = None,
        is_inline: bool = False,
    ) -> dict[str, Any]:
        """
        Create a new database.

        Args:
            parent: Parent page reference.
            title: Database title as rich text array.
            properties: Database property schema.
            icon: Optional database icon.
            cover: Optional database cover.
            is_inline: Whether the database is inline.

        Returns:
            Created database object.
        """
        payload: dict[str, Any] = {
            "parent": parent,
            "title": title,
            "properties": properties,
            "is_inline": is_inline,
        }
        if icon:
            payload["icon"] = icon
        if cover:
            payload["cover"] = cover

        return self.client.post("/databases", json_data=payload)

    def update(
        self,
        database_id: str,
        title: list[dict[str, Any]] | None = None,
        description: list[dict[str, Any]] | None = None,
        properties: dict[str, Any] | None = None,
        icon: dict[str, Any] | None = None,
        cover: dict[str, Any] | None = None,
        archived: bool | None = None,
    ) -> dict[str, Any]:
        """
        Update a database.

        Args:
            database_id: The ID of the database to update.
            title: New database title.
            description: New database description.
            properties: Property schema updates.
            icon: Database icon to set.
            cover: Database cover to set.
            archived: Whether to archive the database.

        Returns:
            Updated database object.
        """
        payload: dict[str, Any] = {}
        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if properties is not None:
            payload["properties"] = properties
        if icon is not None:
            payload["icon"] = icon
        if cover is not None:
            payload["cover"] = cover
        if archived is not None:
            payload["archived"] = archived

        return self.client.patch(f"/databases/{database_id}", json_data=payload)

    def close(self) -> None:
        """Close the API client."""
        self.client.close()
