"""CLI commands for Blocks API."""

from __future__ import annotations

import json

import click

from notion_cli.api.blocks import BlocksAPI
from notion_cli.config import OutputFormat
from notion_cli.output.formatters import format_list, format_output

# Shared format option for commands
FORMAT_OPTION = click.option(
    "--format", "-f", "local_format",
    type=click.Choice(["json", "pretty", "compact", "markdown"]),
    help="Output format (overrides global --format)",
)


@click.group()
def blocks() -> None:
    """Manage Notion blocks."""
    pass


@blocks.command("get")
@click.argument("block_id")
@FORMAT_OPTION
@click.pass_context
def get_block(ctx: click.Context, block_id: str, local_format: str | None) -> None:
    """Retrieve a block by ID."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = BlocksAPI(settings)
    try:
        result = api.retrieve(block_id)
        click.echo(format_output(result, output_format))
    finally:
        api.close()


@blocks.command("children")
@click.argument("block_id")
@click.option("--recursive", is_flag=True, help="Recursively fetch all nested children")
@click.option("--page-size", type=int, help="Number of results per page")
@click.option("--max-depth", type=int, help="Maximum nesting depth (0 = top-level only)")
@FORMAT_OPTION
@click.pass_context
def get_children(
    ctx: click.Context,
    block_id: str,
    recursive: bool,
    page_size: int | None,
    max_depth: int | None,
    local_format: str | None,
) -> None:
    """Get block children."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = BlocksAPI(settings)

    try:
        if recursive:
            results = api.retrieve_children_all(
                block_id, recursive=True, max_depth=max_depth
            )
            click.echo(format_list(results, output_format))
        else:
            result = api.retrieve_children(block_id, page_size=page_size)
            click.echo(format_output(result, output_format))
    finally:
        api.close()


@blocks.command("append")
@click.argument("block_id")
@click.option("--content", required=True, help="JSON array of block children to append")
@click.option("--after", help="Block ID to insert after")
@FORMAT_OPTION
@click.pass_context
def append_children(
    ctx: click.Context,
    block_id: str,
    content: str,
    after: str | None,
    local_format: str | None,
) -> None:
    """Append children to a block."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = BlocksAPI(settings)

    try:
        children = json.loads(content)
        result = api.append_children(block_id, children, after=after)
        click.echo(format_output(result, output_format))
    finally:
        api.close()


@blocks.command("update")
@click.argument("block_id")
@click.option("--content", required=True, help="JSON block data to update")
@FORMAT_OPTION
@click.pass_context
def update_block(
    ctx: click.Context,
    block_id: str,
    content: str,
    local_format: str | None,
) -> None:
    """Update a block."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = BlocksAPI(settings)

    try:
        block_data = json.loads(content)
        result = api.update(block_id, block_data)
        click.echo(format_output(result, output_format))
    finally:
        api.close()


@blocks.command("delete")
@click.argument("block_id")
@FORMAT_OPTION
@click.pass_context
def delete_block(
    ctx: click.Context, block_id: str, local_format: str | None
) -> None:
    """Delete (archive) a block."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = BlocksAPI(settings)
    try:
        result = api.delete(block_id)
        click.echo(format_output(result, output_format))
    finally:
        api.close()
