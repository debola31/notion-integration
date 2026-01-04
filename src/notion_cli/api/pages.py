"""Pages API operations."""

from __future__ import annotations

import re
from typing import Any

from notion_cli.client.base import NotionClient
from notion_cli.config import Settings


# Block types that contain rich_text content
RICH_TEXT_BLOCK_TYPES = {
    "paragraph": "paragraph",
    "heading_1": "heading_1",
    "heading_2": "heading_2",
    "heading_3": "heading_3",
    "bulleted_list_item": "bulleted_list_item",
    "numbered_list_item": "numbered_list_item",
    "to_do": "to_do",
    "toggle": "toggle",
    "quote": "quote",
    "callout": "callout",
}

# Code blocks have a different structure
CODE_BLOCK_TYPE = "code"


def _get_plain_text(rich_text: list[dict[str, Any]]) -> str:
    """Extract plain text from a rich_text array."""
    return "".join(segment.get("plain_text", "") for segment in rich_text)


def _search_in_rich_text(
    rich_text: list[dict[str, Any]],
    find_text: str,
    ignore_case: bool = False,
) -> list[tuple[int, int]]:
    """
    Find all occurrences of text in rich_text.

    Returns list of (start, end) positions in the plain text.
    """
    plain = _get_plain_text(rich_text)
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.escape(find_text)
    return [(m.start(), m.end()) for m in re.finditer(pattern, plain, flags)]


def _replace_in_rich_text(
    rich_text: list[dict[str, Any]],
    find_text: str,
    replace_text: str,
    ignore_case: bool = False,
) -> list[dict[str, Any]]:
    """
    Replace text in rich_text array.

    This simplifies the rich_text to a single text segment with the replacement.
    Formatting is preserved where possible, but complex formatting may be simplified.
    """
    plain = _get_plain_text(rich_text)
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.escape(find_text)
    new_text = re.sub(pattern, replace_text, plain, flags=flags)

    # Return as a simple text segment
    # This preserves the content but may lose some formatting
    return [{"type": "text", "text": {"content": new_text}}]


def _get_context(text: str, start: int, end: int, context_chars: int = 30) -> str:
    """Get text surrounding a match for display."""
    ctx_start = max(0, start - context_chars)
    ctx_end = min(len(text), end + context_chars)

    prefix = "..." if ctx_start > 0 else ""
    suffix = "..." if ctx_end < len(text) else ""

    before = text[ctx_start:start]
    match = text[start:end]
    after = text[end:ctx_end]

    return f"{prefix}{before}[{match}]{after}{suffix}"


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

    def move(
        self,
        page_id: str,
        parent: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Move a page to a new parent.

        Uses the dedicated move endpoint: POST /pages/{page_id}/move

        Args:
            page_id: The ID of the page to move.
            parent: New parent reference with type field:
                - {"type": "page_id", "page_id": "xxx"} for page parent
                - {"type": "database_id", "database_id": "xxx"} for database parent
                - {"type": "workspace", "workspace": true} for workspace (top-level)

        Returns:
            Updated page object.
        """
        payload = {"parent": parent}
        return self.client.post(f"/pages/{page_id}/move", json_data=payload)

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

    def find_replace(
        self,
        page_id: str,
        find_text: str,
        replace_text: str | None = None,
        ignore_case: bool = False,
    ) -> dict[str, Any]:
        """
        Find and optionally replace text in a page's blocks.

        Args:
            page_id: The page to search.
            find_text: Text to find.
            replace_text: Text to replace with (None = dry-run/find only).
            ignore_case: Case-insensitive matching.

        Returns:
            Results with matches found and blocks modified.
        """
        from notion_cli.api.blocks import BlocksAPI

        blocks_api = BlocksAPI(self.client.settings)
        try:
            # Fetch all blocks recursively
            all_blocks = blocks_api.retrieve_children_all(page_id, recursive=True)

            matches: list[dict[str, Any]] = []
            blocks_modified = 0

            # Process blocks (including nested children)
            self._process_blocks_for_replace(
                blocks_api,
                all_blocks,
                find_text,
                replace_text,
                ignore_case,
                matches,
            )

            # Count blocks actually modified
            if replace_text is not None:
                blocks_modified = sum(1 for m in matches if m.get("replaced", False))

            return {
                "page_id": page_id,
                "find": find_text,
                "replace": replace_text,
                "matches": matches,
                "total_matches": len(matches),
                "blocks_modified": blocks_modified,
            }
        finally:
            blocks_api.close()

    def _process_blocks_for_replace(
        self,
        blocks_api: Any,
        blocks: list[dict[str, Any]],
        find_text: str,
        replace_text: str | None,
        ignore_case: bool,
        matches: list[dict[str, Any]],
    ) -> None:
        """Process a list of blocks for find/replace."""
        for block in blocks:
            block_type = block.get("type", "")
            block_id = block.get("id", "")

            # Get rich_text based on block type
            rich_text = None
            type_key = None

            if block_type in RICH_TEXT_BLOCK_TYPES:
                type_key = RICH_TEXT_BLOCK_TYPES[block_type]
                block_content = block.get(type_key, {})
                rich_text = block_content.get("rich_text", [])
            elif block_type == CODE_BLOCK_TYPE:
                type_key = CODE_BLOCK_TYPE
                block_content = block.get(type_key, {})
                rich_text = block_content.get("rich_text", [])

            # Search in rich_text if present
            if rich_text:
                found_positions = _search_in_rich_text(rich_text, find_text, ignore_case)

                if found_positions:
                    plain_text = _get_plain_text(rich_text)

                    for start, end in found_positions:
                        context = _get_context(plain_text, start, end)
                        match_info: dict[str, Any] = {
                            "block_id": block_id,
                            "block_type": block_type,
                            "context": context,
                            "replaced": False,
                        }

                        # Perform replacement if not dry-run
                        if replace_text is not None and type_key:
                            new_rich_text = _replace_in_rich_text(
                                rich_text, find_text, replace_text, ignore_case
                            )
                            # Build update payload
                            update_data = {
                                type_key: {"rich_text": new_rich_text}
                            }
                            # For to_do, preserve checked state
                            if block_type == "to_do":
                                checked = block.get("to_do", {}).get("checked", False)
                                update_data["to_do"]["checked"] = checked

                            blocks_api.update(block_id, update_data)
                            match_info["replaced"] = True
                            # Update rich_text to prevent duplicate replacements
                            rich_text = new_rich_text

                        matches.append(match_info)

            # Process nested children
            children = block.get("children", [])
            if children:
                self._process_blocks_for_replace(
                    blocks_api, children, find_text, replace_text, ignore_case, matches
                )
