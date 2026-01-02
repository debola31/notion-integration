"""CLI commands for Databases API."""

from __future__ import annotations

import json
from typing import Any

import click

from notion_cli.api.databases import DatabasesAPI
from notion_cli.output.formatters import format_list, format_output


@click.group()
def databases() -> None:
    """Manage Notion databases."""
    pass


@databases.command("get")
@click.argument("database_id")
@click.pass_context
def get_database(ctx: click.Context, database_id: str) -> None:
    """Retrieve a database by ID."""
    settings = ctx.obj["settings"]
    api = DatabasesAPI(settings)
    try:
        result = api.retrieve(database_id)
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()


@databases.command("query")
@click.argument("database_id")
@click.option("--filter", "filter_json", help="JSON filter object")
@click.option("--filter-file", type=click.Path(exists=True), help="Path to JSON filter file")
@click.option("--sort", "sort_json", help="JSON sort array")
@click.option("--page-size", type=int, help="Number of results per page (max 100)")
@click.option("--all", "fetch_all", is_flag=True, help="Fetch all results (handle pagination)")
@click.pass_context
def query_database(
    ctx: click.Context,
    database_id: str,
    filter_json: str | None,
    filter_file: str | None,
    sort_json: str | None,
    page_size: int | None,
    fetch_all: bool,
) -> None:
    """Query a database."""
    settings = ctx.obj["settings"]
    api = DatabasesAPI(settings)

    try:
        # Parse filter
        filter_obj: dict[str, Any] | None = None
        if filter_file:
            with open(filter_file) as f:
                filter_obj = json.load(f)
        elif filter_json:
            filter_obj = json.loads(filter_json)

        # Parse sort
        sorts: list[dict[str, Any]] | None = None
        if sort_json:
            sorts = json.loads(sort_json)

        if fetch_all:
            results = api.query_all(
                database_id,
                filter_obj=filter_obj,
                sorts=sorts,
            )
            click.echo(format_list(results, settings.output_format))
        else:
            result = api.query(
                database_id,
                filter_obj=filter_obj,
                sorts=sorts,
                page_size=page_size,
            )
            click.echo(format_output(result, settings.output_format))
    finally:
        api.close()


@databases.command("create")
@click.option("--parent-id", required=True, help="Parent page ID")
@click.option("--title", required=True, help="Database title")
@click.option("--properties", required=True, help="JSON properties schema")
@click.option("--inline", is_flag=True, help="Create as inline database")
@click.pass_context
def create_database(
    ctx: click.Context,
    parent_id: str,
    title: str,
    properties: str,
    inline: bool,
) -> None:
    """Create a new database."""
    settings = ctx.obj["settings"]
    api = DatabasesAPI(settings)

    try:
        title_rich_text = [{"type": "text", "text": {"content": title}}]
        props = json.loads(properties)

        result = api.create(
            parent={"page_id": parent_id},
            title=title_rich_text,
            properties=props,
            is_inline=inline,
        )
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()


@databases.command("update")
@click.argument("database_id")
@click.option("--title", help="New database title")
@click.option("--description", help="New database description")
@click.option("--properties", help="JSON properties schema updates")
@click.pass_context
def update_database(
    ctx: click.Context,
    database_id: str,
    title: str | None,
    description: str | None,
    properties: str | None,
) -> None:
    """Update a database."""
    settings = ctx.obj["settings"]
    api = DatabasesAPI(settings)

    try:
        title_rich_text = None
        if title:
            title_rich_text = [{"type": "text", "text": {"content": title}}]

        desc_rich_text = None
        if description:
            desc_rich_text = [{"type": "text", "text": {"content": description}}]

        props = json.loads(properties) if properties else None

        result = api.update(
            database_id,
            title=title_rich_text,
            description=desc_rich_text,
            properties=props,
        )
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()
