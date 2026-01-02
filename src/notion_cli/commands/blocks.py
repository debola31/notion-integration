"""CLI commands for Blocks API."""

from __future__ import annotations

import json

import click

from notion_cli.api.blocks import BlocksAPI
from notion_cli.output.formatters import format_list, format_output


@click.group()
def blocks() -> None:
    """Manage Notion blocks."""
    pass


@blocks.command("get")
@click.argument("block_id")
@click.pass_context
def get_block(ctx: click.Context, block_id: str) -> None:
    """Retrieve a block by ID."""
    settings = ctx.obj["settings"]
    api = BlocksAPI(settings)
    try:
        result = api.retrieve(block_id)
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()


@blocks.command("children")
@click.argument("block_id")
@click.option("--recursive", is_flag=True, help="Recursively fetch all nested children")
@click.option("--page-size", type=int, help="Number of results per page")
@click.pass_context
def get_children(
    ctx: click.Context,
    block_id: str,
    recursive: bool,
    page_size: int | None,
) -> None:
    """Get block children."""
    settings = ctx.obj["settings"]
    api = BlocksAPI(settings)

    try:
        if recursive:
            results = api.retrieve_children_all(block_id, recursive=True)
            click.echo(format_list(results, settings.output_format))
        else:
            result = api.retrieve_children(block_id, page_size=page_size)
            click.echo(format_output(result, settings.output_format))
    finally:
        api.close()


@blocks.command("append")
@click.argument("block_id")
@click.option("--content", required=True, help="JSON array of block children to append")
@click.option("--after", help="Block ID to insert after")
@click.pass_context
def append_children(
    ctx: click.Context,
    block_id: str,
    content: str,
    after: str | None,
) -> None:
    """Append children to a block."""
    settings = ctx.obj["settings"]
    api = BlocksAPI(settings)

    try:
        children = json.loads(content)
        result = api.append_children(block_id, children, after=after)
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()


@blocks.command("update")
@click.argument("block_id")
@click.option("--content", required=True, help="JSON block data to update")
@click.pass_context
def update_block(
    ctx: click.Context,
    block_id: str,
    content: str,
) -> None:
    """Update a block."""
    settings = ctx.obj["settings"]
    api = BlocksAPI(settings)

    try:
        block_data = json.loads(content)
        result = api.update(block_id, block_data)
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()


@blocks.command("delete")
@click.argument("block_id")
@click.pass_context
def delete_block(ctx: click.Context, block_id: str) -> None:
    """Delete (archive) a block."""
    settings = ctx.obj["settings"]
    api = BlocksAPI(settings)
    try:
        result = api.delete(block_id)
        click.echo(format_output(result, settings.output_format))
    finally:
        api.close()
