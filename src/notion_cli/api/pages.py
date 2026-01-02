"""Pages API operations."""

from __future__ import annotations

from typing import Any

from notion_cli.client.base import NotionClient
from notion_cli.config import Settings


class PagesAPI:
    """API client for Notion Pages."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the Pages API client."""
        self.client = NotionClient(settings)

    def retrieve(self, page_id: str) -> dict[str, Any]:
        """
        Retrieve a page by ID.

        Args:
            page_id: The ID of the page to retrieve.

        Returns:
            Page object.
        """
        return self.client.get(f"/pages/{page_id}")

    def create(
        self,
        parent: dict[str, Any],
        properties: dict[str, Any],
        children: list[dict[str, Any]] | None = None,
        icon: dict[str, Any] | None = None,
        cover: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new page.

        Args:
            parent: Parent page or database reference.
            properties: Page properties.
            children: Optional list of block children.
            icon: Optional page icon.
            cover: Optional page cover.

        Returns:
            Created page object.
        """
        payload: dict[str, Any] = {
            "parent": parent,
            "properties": properties,
        }
        if children:
            payload["children"] = children
        if icon:
            payload["icon"] = icon
        if cover:
            payload["cover"] = cover

        return self.client.post("/pages", json_data=payload)

    def update(
        self,
        page_id: str,
        properties: dict[str, Any] | None = None,
        archived: bool | None = None,
        icon: dict[str, Any] | None = None,
        cover: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Update a page.

        Args:
            page_id: The ID of the page to update.
            properties: Page properties to update.
            archived: Whether to archive the page.
            icon: Page icon to set.
            cover: Page cover to set.

        Returns:
            Updated page object.
        """
        payload: dict[str, Any] = {}
        if properties is not None:
            payload["properties"] = properties
        if archived is not None:
            payload["archived"] = archived
        if icon is not None:
            payload["icon"] = icon
        if cover is not None:
            payload["cover"] = cover

        return self.client.patch(f"/pages/{page_id}", json_data=payload)

    def archive(self, page_id: str) -> dict[str, Any]:
        """
        Archive a page.

        Args:
            page_id: The ID of the page to archive.

        Returns:
            Archived page object.
        """
        return self.update(page_id, archived=True)

    def restore(self, page_id: str) -> dict[str, Any]:
        """
        Restore an archived page.

        Args:
            page_id: The ID of the page to restore.

        Returns:
            Restored page object.
        """
        return self.update(page_id, archived=False)

    def retrieve_property(
        self,
        page_id: str,
        property_id: str,
        start_cursor: str | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve a page property item.

        Args:
            page_id: The ID of the page.
            property_id: The ID of the property to retrieve.
            start_cursor: Cursor for pagination.
            page_size: Number of items to return.

        Returns:
            Property item or list of property items.
        """
        params: dict[str, Any] = {}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size

        return self.client.get(
            f"/pages/{page_id}/properties/{property_id}",
            params=params if params else None,
        )

    def close(self) -> None:
        """Close the API client."""
        self.client.close()
