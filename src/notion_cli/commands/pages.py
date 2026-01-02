"""CLI commands for Pages API."""

from __future__ import annotations

import json
from typing import Any

import click

from notion_cli.api.pages import PagesAPI
from notion_cli.output.formatters import format_output


@click.group()
def pages() -> None:
    """Manage Notion pages."""
    pass


@pages.command("get")
@click.argument("page_id")
@click.pass_context
def get_page(ctx: click.Context, page_id: str) -> None:
    """Retrieve a page by ID."""
    settings = ctx.obj["settings"]
    api = PagesAPI(settings)
    try:
        result = api.retrieve(page_id)
        click.echo(format_output(result, settings.output_format))
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
) -> None:
    """Create a new page."""
    settings = ctx.obj["settings"]
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
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()


@pages.command("update")
@click.argument("page_id")
@click.option("--properties", help="JSON properties object to update")
@click.option("--icon", help="JSON icon object")
@click.option("--cover", help="JSON cover object")
@click.pass_context
def update_page(
    ctx: click.Context,
    page_id: str,
    properties: str | None,
    icon: str | None,
    cover: str | None,
) -> None:
    """Update a page."""
    settings = ctx.obj["settings"]
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
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()


@pages.command("archive")
@click.argument("page_id")
@click.pass_context
def archive_page(ctx: click.Context, page_id: str) -> None:
    """Archive a page."""
    settings = ctx.obj["settings"]
    api = PagesAPI(settings)
    try:
        result = api.archive(page_id)
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()


@pages.command("restore")
@click.argument("page_id")
@click.pass_context
def restore_page(ctx: click.Context, page_id: str) -> None:
    """Restore an archived page."""
    settings = ctx.obj["settings"]
    api = PagesAPI(settings)
    try:
        result = api.restore(page_id)
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()


@pages.command("property")
@click.argument("page_id")
@click.argument("property_id")
@click.pass_context
def get_property(ctx: click.Context, page_id: str, property_id: str) -> None:
    """Retrieve a page property."""
    settings = ctx.obj["settings"]
    api = PagesAPI(settings)
    try:
        result = api.retrieve_property(page_id, property_id)
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()
