"""CLI commands for Search API."""

from __future__ import annotations

from typing import Any, Literal

import click

from notion_cli.api.search import SearchAPI
from notion_cli.config import OutputFormat
from notion_cli.output.formatters import format_list, format_output


def _extract_title(item: dict[str, Any]) -> str:
    """Extract title from a page or database object."""
    if item.get("object") == "page":
        props = item.get("properties", {})
        for prop in props.values():
            if prop.get("type") == "title":
                title_array = prop.get("title", [])
                return "".join(t.get("plain_text", "") for t in title_array)
    elif item.get("object") == "database":
        title_array = item.get("title", [])
        return "".join(t.get("plain_text", "") for t in title_array)
    return "Untitled"


@click.command()
@click.argument("query", required=False)
@click.option("--filter", "filter_type", type=click.Choice(["page", "database"]),
              help="Filter by object type")
@click.option("--sort", "sort_direction", type=click.Choice(["ascending", "descending"]),
              help="Sort direction by last edited time")
@click.option("--page-size", type=int, help="Number of results per page")
@click.option("--all", "fetch_all", is_flag=True, help="Fetch all results (handle pagination)")
@click.option("--quiet", "-q", is_flag=True, help="Output only id<tab>title per line")
@click.option("--format", "-f", "local_format",
              type=click.Choice(["json", "pretty", "compact", "markdown"]),
              help="Output format (overrides global --format)")
@click.pass_context
def search(
    ctx: click.Context,
    query: str | None,
    filter_type: Literal["page", "database"] | None,
    sort_direction: Literal["ascending", "descending"] | None,
    page_size: int | None,
    fetch_all: bool,
    quiet: bool,
    local_format: str | None,
) -> None:
    """Search for pages and databases."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = SearchAPI(settings)

    try:
        sort_timestamp: Literal["last_edited_time"] | None = None
        if sort_direction:
            sort_timestamp = "last_edited_time"

        if fetch_all:
            results = api.search_all(
                query=query,
                filter_type=filter_type,
                sort_direction=sort_direction,
                sort_timestamp=sort_timestamp,
            )
            if quiet:
                for item in results:
                    item_id = item.get("id", "")
                    title = _extract_title(item)
                    click.echo(f"{item_id}\t{title}")
            else:
                click.echo(format_list(results, output_format))
        else:
            result = api.search(
                query=query,
                filter_type=filter_type,
                sort_direction=sort_direction,
                sort_timestamp=sort_timestamp,
                page_size=page_size,
            )
            if quiet:
                items = result.get("results", [])
                for item in items:
                    item_id = item.get("id", "")
                    title = _extract_title(item)
                    click.echo(f"{item_id}\t{title}")
            else:
                click.echo(format_output(result, output_format))
    finally:
        api.close()
