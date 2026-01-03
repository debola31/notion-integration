"""CLI commands for Comments API."""

from __future__ import annotations

import click

from notion_cli.api.comments import CommentsAPI
from notion_cli.config import OutputFormat
from notion_cli.output.formatters import format_list, format_output

# Shared format option for commands
FORMAT_OPTION = click.option(
    "--format", "-f", "local_format",
    type=click.Choice(["json", "pretty", "compact", "markdown"]),
    help="Output format (overrides global --format)",
)


@click.group()
def comments() -> None:
    """Manage Notion comments."""
    pass


@comments.command("list")
@click.option("--block-id", required=True, help="Block or page ID to get comments for")
@click.option("--all", "fetch_all", is_flag=True, help="Fetch all comments (handle pagination)")
@click.option("--page-size", type=int, help="Number of results per page")
@FORMAT_OPTION
@click.pass_context
def list_comments(
    ctx: click.Context,
    block_id: str,
    fetch_all: bool,
    page_size: int | None,
    local_format: str | None,
) -> None:
    """List comments for a block or page."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = CommentsAPI(settings)

    try:
        if fetch_all:
            results = api.list_all(block_id)
            click.echo(format_list(results, output_format))
        else:
            result = api.list(block_id=block_id, page_size=page_size)
            click.echo(format_output(result, output_format))
    finally:
        api.close()


@comments.command("create")
@click.option("--page-id", required=True, help="Page ID to comment on")
@click.option("--text", required=True, help="Comment text")
@click.option("--discussion-id", help="Discussion thread ID to reply to")
@FORMAT_OPTION
@click.pass_context
def create_comment(
    ctx: click.Context,
    page_id: str,
    text: str,
    discussion_id: str | None,
    local_format: str | None,
) -> None:
    """Create a new comment."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = CommentsAPI(settings)

    try:
        result = api.create_text(page_id, text, discussion_id=discussion_id)
        click.echo(format_output(result, output_format))
    finally:
        api.close()
