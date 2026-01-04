"""CLI commands for Pages API."""

from __future__ import annotations

import json
from typing import Any

import click

from notion_cli.api.pages import PagesAPI
from notion_cli.config import OutputFormat
from notion_cli.output.formatters import format_output

# Shared format option for commands
FORMAT_OPTION = click.option(
    "--format", "-f", "local_format",
    type=click.Choice(["json", "pretty", "compact", "markdown"]),
    help="Output format (overrides global --format)",
)


@click.group()
def pages() -> None:
    """Manage Notion pages."""
    pass


@pages.command("get")
@click.argument("page_id")
@FORMAT_OPTION
@click.pass_context
def get_page(ctx: click.Context, page_id: str, local_format: str | None) -> None:
    """Retrieve a page by ID.

    \b
    Examples:
        notion pages get abc123-def456
        notion pages get abc123 --format pretty
    """
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = PagesAPI(settings)
    try:
        result = api.retrieve(page_id)
        click.echo(format_output(result, output_format))
    finally:
        api.close()


@pages.command("create")
@click.option("--parent-id", required=True, help="Parent page or database ID")
@click.option("--parent-type", type=click.Choice(["page", "database"]), default="page",
              help="Type of parent")
@click.option("--title", required=True, help="Page title")
@click.option("--properties", help="JSON properties object")
@click.option("--content", help="JSON array of block children")
@click.option("--icon", help="JSON icon object (emoji or external)")
@click.option("--cover", help="JSON cover object (external URL)")
@FORMAT_OPTION
@click.pass_context
def create_page(
    ctx: click.Context,
    parent_id: str,
    parent_type: str,
    title: str,
    properties: str | None,
    content: str | None,
    icon: str | None,
    cover: str | None,
    local_format: str | None,
) -> None:
    """Create a new page.

    \b
    Examples:
        # Create page under another page:
        notion pages create --parent-id abc123 --title "My Page"

        # Create page in a database with properties:
        notion pages create --parent-id db123 --parent-type database \\
            --title "Task" --properties '{"Status": {"select": {"name": "Todo"}}}'

        # Create page with content blocks:
        notion pages create --parent-id abc123 --title "Notes" \\
            --content '[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello"}}]}}]'

        # Create page with emoji icon:
        notion pages create --parent-id abc123 --title "Doc" \\
            --icon '{"type": "emoji", "emoji": "📄"}'
    """
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = PagesAPI(settings)

    try:
        # Build parent reference
        if parent_type == "page":
            parent = {"page_id": parent_id}
        else:
            parent = {"database_id": parent_id}

        # Build properties with title
        props: dict[str, Any] = {}
        if properties:
            props = json.loads(properties)

        # Add title property
        if parent_type == "page":
            props["title"] = {"title": [{"text": {"content": title}}]}
        else:
            # For database pages, use the Name property (common default)
            props["Name"] = {"title": [{"text": {"content": title}}]}

        # Parse optional JSON fields
        children = json.loads(content) if content else None
        icon_obj = json.loads(icon) if icon else None
        cover_obj = json.loads(cover) if cover else None

        result = api.create(
            parent=parent,
            properties=props,
            children=children,
            icon=icon_obj,
            cover=cover_obj,
        )
        click.echo(format_output(result, output_format))
    finally:
        api.close()


@pages.command("update")
@click.argument("page_id")
@click.option("--properties", help="JSON properties object to update")
@click.option("--icon", help="JSON icon object")
@click.option("--cover", help="JSON cover object")
@FORMAT_OPTION
@click.pass_context
def update_page(
    ctx: click.Context,
    page_id: str,
    properties: str | None,
    icon: str | None,
    cover: str | None,
    local_format: str | None,
) -> None:
    """Update a page's properties, icon, or cover.

    \b
    Examples:
        # Update a select property:
        notion pages update abc123 --properties '{"Status": {"select": {"name": "Done"}}}'

        # Update a checkbox property:
        notion pages update abc123 --properties '{"Completed": {"checkbox": true}}'

        # Update multiple properties:
        notion pages update abc123 --properties '{"Status": {"select": {"name": "Done"}}, "Priority": {"select": {"name": "High"}}}'

        # Set emoji icon:
        notion pages update abc123 --icon '{"type": "emoji", "emoji": "✅"}'
    """
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = PagesAPI(settings)

    try:
        props = json.loads(properties) if properties else None
        icon_obj = json.loads(icon) if icon else None
        cover_obj = json.loads(cover) if cover else None

        result = api.update(
            page_id,
            properties=props,
            icon=icon_obj,
            cover=cover_obj,
        )
        click.echo(format_output(result, output_format))
    finally:
        api.close()


@pages.command("archive")
@click.argument("page_id")
@FORMAT_OPTION
@click.pass_context
def archive_page(
    ctx: click.Context, page_id: str, local_format: str | None
) -> None:
    """Archive a page."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = PagesAPI(settings)
    try:
        result = api.archive(page_id)
        click.echo(format_output(result, output_format))
    finally:
        api.close()


@pages.command("restore")
@click.argument("page_id")
@FORMAT_OPTION
@click.pass_context
def restore_page(
    ctx: click.Context, page_id: str, local_format: str | None
) -> None:
    """Restore an archived page."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = PagesAPI(settings)
    try:
        result = api.restore(page_id)
        click.echo(format_output(result, output_format))
    finally:
        api.close()


@pages.command("move")
@click.argument("page_id")
@click.option("--to-page", help="Move under a page (provide page ID)")
@click.option("--to-database", help="Move into a database (provide database ID)")
@click.option("--to-workspace", is_flag=True, help="Move to workspace top-level")
@FORMAT_OPTION
@click.pass_context
def move_page(
    ctx: click.Context,
    page_id: str,
    to_page: str | None,
    to_database: str | None,
    to_workspace: bool,
    local_format: str | None,
) -> None:
    """Move a page to a new parent location.

    \b
    Examples:
        # Move page under another page:
        notion pages move abc123 --to-page def456

        # Move page into a database:
        notion pages move abc123 --to-database db789

        # Move page to workspace root (top-level):
        notion pages move abc123 --to-workspace
    """
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format

    # Validate exactly one destination is specified
    destinations = [to_page, to_database, to_workspace]
    specified = sum(1 for d in destinations if d)
    if specified == 0:
        raise click.UsageError(
            "Must specify one of: --to-page, --to-database, or --to-workspace"
        )
    if specified > 1:
        raise click.UsageError(
            "Cannot specify multiple destinations. Use only one of: "
            "--to-page, --to-database, or --to-workspace"
        )

    # Build parent dict based on option
    if to_page:
        parent: dict[str, Any] = {"page_id": to_page}
    elif to_database:
        parent = {"database_id": to_database}
    else:  # to_workspace
        parent = {"workspace": True}

    api = PagesAPI(settings)
    try:
        result = api.move(page_id, parent)
        click.echo(format_output(result, output_format))
    finally:
        api.close()


@pages.command("property")
@click.argument("page_id")
@click.argument("property_id")
@FORMAT_OPTION
@click.pass_context
def get_property(
    ctx: click.Context, page_id: str, property_id: str, local_format: str | None
) -> None:
    """Retrieve a page property."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = PagesAPI(settings)
    try:
        result = api.retrieve_property(page_id, property_id)
        click.echo(format_output(result, output_format))
    finally:
        api.close()
