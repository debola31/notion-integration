"""CLI commands for Search API."""

from __future__ import annotations

from typing import Literal

import click

from notion_cli.api.search import SearchAPI
from notion_cli.output.formatters import format_list, format_output


@click.command()
@click.argument("query", required=False)
@click.option("--filter", "filter_type", type=click.Choice(["page", "database"]),
              help="Filter by object type")
@click.option("--sort", "sort_direction", type=click.Choice(["ascending", "descending"]),
              help="Sort direction by last edited time")
@click.option("--page-size", type=int, help="Number of results per page")
@click.option("--all", "fetch_all", is_flag=True, help="Fetch all results (handle pagination)")
@click.pass_context
def search(
    ctx: click.Context,
    query: str | None,
    filter_type: Literal["page", "database"] | None,
    sort_direction: Literal["ascending", "descending"] | None,
    page_size: int | None,
    fetch_all: bool,
) -> None:
    """Search for pages and databases."""
    settings = ctx.obj["settings"]
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
            click.echo(format_list(results, settings.output_format))
        else:
            result = api.search(
                query=query,
                filter_type=filter_type,
                sort_direction=sort_direction,
                sort_timestamp=sort_timestamp,
                page_size=page_size,
            )
            click.echo(format_output(result, settings.output_format))
    finally:
        api.close()
