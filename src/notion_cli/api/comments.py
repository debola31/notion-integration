"""Comments API operations."""

from __future__ import annotations

from typing import Any

from notion_cli.client.base import NotionClient
from notion_cli.config import Settings


class CommentsAPI:
    """API client for Notion Comments."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the Comments API client."""
        self.client = NotionClient(settings)

    def list(
        self,
        block_id: str | None = None,
        start_cursor: str | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        List comments for a block or page.

        Args:
            block_id: The ID of the block/page to get comments for.
            start_cursor: Cursor for pagination.
            page_size: Number of results to return.

        Returns:
            List of comment objects.
        """
        params: dict[str, Any] = {}
        if block_id:
            params["block_id"] = block_id
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size

        return self.client.get("/comments", params=params if params else None)

    def list_all(self, block_id: str) -> list[dict[str, Any]]:
        """
        List all comments for a block (handles pagination).

        Args:
            block_id: The ID of the block/page to get comments for.

        Returns:
            List of all comment objects.
        """
        all_comments: list[dict[str, Any]] = []
        start_cursor: str | None = None

        while True:
            response = self.list(
                block_id=block_id,
                start_cursor=start_cursor,
                page_size=100,
            )
            all_comments.extend(response.get("results", []))

            if not response.get("has_more", False):
                break
            start_cursor = response.get("next_cursor")

        return all_comments

    def create(
        self,
        parent: dict[str, Any],
        rich_text: list[dict[str, Any]],
        discussion_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new comment.

        Args:
            parent: Parent page reference {"page_id": "..."}.
            rich_text: Comment content as rich text array.
            discussion_id: Optional discussion thread ID to reply to.

        Returns:
            Created comment object.
        """
        payload: dict[str, Any] = {
            "parent": parent,
            "rich_text": rich_text,
        }
        if discussion_id:
            payload["discussion_id"] = discussion_id

        return self.client.post("/comments", json_data=payload)

    def create_text(
        self,
        page_id: str,
        text: str,
        discussion_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new comment with plain text (convenience method).

        Args:
            page_id: The ID of the page to comment on.
            text: Plain text comment content.
            discussion_id: Optional discussion thread ID to reply to.

        Returns:
            Created comment object.
        """
        return self.create(
            parent={"page_id": page_id},
            rich_text=[{"type": "text", "text": {"content": text}}],
            discussion_id=discussion_id,
        )

    def close(self) -> None:
        """Close the API client."""
        self.client.close()
