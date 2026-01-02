"""Output formatting utilities."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from notion_cli.config import OutputFormat


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
