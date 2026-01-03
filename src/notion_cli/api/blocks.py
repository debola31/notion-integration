"""Blocks API operations."""

from __future__ import annotations

from typing import Any

from notion_cli.client.base import NotionClient
from notion_cli.config import Settings


class BlocksAPI:
    """API client for Notion Blocks."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the Blocks API client."""
        self.client = NotionClient(settings)

    def retrieve(self, block_id: str) -> dict[str, Any]:
        """
        Retrieve a block by ID.

        Args:
            block_id: The ID of the block to retrieve.

        Returns:
            Block object.
        """
        return self.client.get(f"/blocks/{block_id}")

    def update(
        self,
        block_id: str,
        block_data: dict[str, Any],
        archived: bool | None = None,
    ) -> dict[str, Any]:
        """
        Update a block.

        Args:
            block_id: The ID of the block to update.
            block_data: Block type-specific data to update.
            archived: Whether to archive the block.

        Returns:
            Updated block object.
        """
        payload = block_data.copy()
        if archived is not None:
            payload["archived"] = archived

        return self.client.patch(f"/blocks/{block_id}", json_data=payload)

    def delete(self, block_id: str) -> dict[str, Any]:
        """
        Delete (archive) a block.

        Args:
            block_id: The ID of the block to delete.

        Returns:
            Deleted block object.
        """
        return self.client.delete(f"/blocks/{block_id}")

    def retrieve_children(
        self,
        block_id: str,
        start_cursor: str | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve block children.

        Args:
            block_id: The ID of the parent block.
            start_cursor: Cursor for pagination.
            page_size: Number of results to return.

        Returns:
            List of child blocks.
        """
        params: dict[str, Any] = {}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size

        return self.client.get(
            f"/blocks/{block_id}/children",
            params=params if params else None,
        )

    def retrieve_children_all(
        self,
        block_id: str,
        recursive: bool = False,
        max_depth: int | None = None,
        _current_depth: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Retrieve all block children (handles pagination).

        Args:
            block_id: The ID of the parent block.
            recursive: Whether to recursively fetch children of children.
            max_depth: Maximum nesting depth to fetch (None = unlimited).
            _current_depth: Internal parameter for tracking recursion depth.

        Returns:
            List of all child blocks.
        """
        # Stop recursing if max_depth reached
        if max_depth is not None and _current_depth > max_depth:
            return []

        all_children: list[dict[str, Any]] = []
        start_cursor: str | None = None

        while True:
            response = self.retrieve_children(
                block_id,
                start_cursor=start_cursor,
                page_size=100,
            )
            children = response.get("results", [])

            if recursive:
                for child in children:
                    if child.get("has_children", False):
                        child["children"] = self.retrieve_children_all(
                            child["id"],
                            recursive=True,
                            max_depth=max_depth,
                            _current_depth=_current_depth + 1,
                        )

            all_children.extend(children)

            if not response.get("has_more", False):
                break
            start_cursor = response.get("next_cursor")

        return all_children

    def append_children(
        self,
        block_id: str,
        children: list[dict[str, Any]],
        after: str | None = None,
    ) -> dict[str, Any]:
        """
        Append children to a block.

        Args:
            block_id: The ID of the parent block.
            children: List of block objects to append.
            after: ID of block to insert after.

        Returns:
            Response with appended block children.
        """
        payload: dict[str, Any] = {"children": children}
        if after:
            payload["after"] = after

        return self.client.patch(
            f"/blocks/{block_id}/children",
            json_data=payload,
        )

    def close(self) -> None:
        """Close the API client."""
        self.client.close()
