"""Output formatting utilities."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from notion_cli.config import OutputFormat
from notion_cli.output.markdown import MarkdownRenderer


def format_output(
    data: Any,
    output_format: OutputFormat = "json",
    cached: bool = False,
    request_id: str | None = None,
) -> str:
    """
    Format API response data for output.

    Args:
        data: Response data to format.
        output_format: Output format type.
        cached: Whether the response was from cache.
        request_id: Request ID from API response.

    Returns:
        Formatted string output.
    """
    if output_format == "markdown":
        return format_as_markdown(data)

    output: dict[str, Any] = {
        "success": True,
        "data": data,
        "metadata": {
            "cached": cached,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    if request_id:
        output["metadata"]["request_id"] = request_id

    return _format_json(output, output_format)


def format_error(
    error: Exception,
    output_format: OutputFormat = "json",
) -> str:
    """
    Format an error for output.

    Args:
        error: The exception to format.
        output_format: Output format type.

    Returns:
        Formatted error string.
    """
    from notion_cli.exceptions import NotionCLIError

    if isinstance(error, NotionCLIError):
        output = error.to_dict()
    else:
        output = {
            "error": True,
            "code": "unexpected_error",
            "message": str(error),
        }

    return _format_json(output, output_format)


def format_list(
    items: list[Any],
    output_format: OutputFormat = "json",
    has_more: bool = False,
    next_cursor: str | None = None,
) -> str:
    """
    Format a list of items for output.

    Args:
        items: List of items to format.
        output_format: Output format type.
        has_more: Whether there are more results.
        next_cursor: Cursor for next page.

    Returns:
        Formatted string output.
    """
    if output_format == "markdown":
        return format_as_markdown_list(items)

    output: dict[str, Any] = {
        "success": True,
        "data": {
            "results": items,
            "count": len(items),
        },
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    if has_more:
        output["data"]["has_more"] = True
        output["data"]["next_cursor"] = next_cursor

    return _format_json(output, output_format)


def _format_json(data: dict[str, Any], output_format: OutputFormat) -> str:
    """Format a dictionary as JSON string."""
    if output_format == "pretty":
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif output_format == "compact":
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    else:  # json (default)
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def format_as_markdown(data: Any) -> str:
    """
    Render data as markdown if it contains blocks.

    Args:
        data: API response data (block, page, or list of blocks).

    Returns:
        Markdown string or simple text representation.
    """
    renderer = MarkdownRenderer()

    # Handle different data shapes
    if isinstance(data, dict):
        # Single block
        if data.get("object") == "block":
            return renderer.render_block(data)
        # Paginated response with results
        if "results" in data and isinstance(data["results"], list):
            return renderer.render_blocks(data["results"])
        # Page object - just return title for now
        if data.get("object") == "page":
            return _extract_page_title(data) + "\n"

    # List of items
    if isinstance(data, list):
        # Check if it's a list of blocks
        if data and isinstance(data[0], dict) and data[0].get("object") == "block":
            return renderer.render_blocks(data)
        # Otherwise render each item
        return _render_items_as_markdown(data)

    # Fallback for non-block data
    return str(data)


def format_as_markdown_list(items: list[Any]) -> str:
    """
    Render a list of items as markdown.

    Args:
        items: List of items (blocks, pages, etc.).

    Returns:
        Markdown string.
    """
    if not items:
        return ""

    renderer = MarkdownRenderer()

    # Check if it's a list of blocks
    if items and isinstance(items[0], dict):
        first_item = items[0]
        if first_item.get("object") == "block" or first_item.get("type"):
            return renderer.render_blocks(items)

    # Otherwise render as list of items
    return _render_items_as_markdown(items)


def _render_items_as_markdown(items: list[Any]) -> str:
    """Render a list of non-block items as markdown."""
    lines: list[str] = []
    for item in items:
        if isinstance(item, dict):
            # Page or database
            if item.get("object") == "page":
                title = _extract_page_title(item)
                url = item.get("url", "")
                lines.append(f"- [{title}]({url})")
            elif item.get("object") == "database":
                title = _extract_database_title(item)
                url = item.get("url", "")
                lines.append(f"- [Database: {title}]({url})")
            else:
                # Generic dict
                lines.append(f"- {item}")
        else:
            lines.append(f"- {item}")
    return "\n".join(lines) + "\n" if lines else ""


def _extract_page_title(page: dict[str, Any]) -> str:
    """Extract title from a page object."""
    props = page.get("properties", {})
    for prop in props.values():
        if prop.get("type") == "title":
            title_array = prop.get("title", [])
            return "".join(t.get("plain_text", "") for t in title_array)
    return "Untitled"


def _extract_database_title(db: dict[str, Any]) -> str:
    """Extract title from a database object."""
    title_array = db.get("title", [])
    return "".join(t.get("plain_text", "") for t in title_array) or "Untitled"

