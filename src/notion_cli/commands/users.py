"""CLI commands for Users API."""

from __future__ import annotations

import click

from notion_cli.api.users import UsersAPI
from notion_cli.config import OutputFormat
from notion_cli.output.formatters import format_list, format_output

# Shared format option for commands
FORMAT_OPTION = click.option(
    "--format", "-f", "local_format",
    type=click.Choice(["json", "pretty", "compact", "markdown"]),
    help="Output format (overrides global --format)",
)


@click.group()
def users() -> None:
    """Manage Notion users."""
    pass


@users.command("list")
@click.option("--all", "fetch_all", is_flag=True, help="Fetch all users (handle pagination)")
@click.option("--page-size", type=int, help="Number of results per page")
@FORMAT_OPTION
@click.pass_context
def list_users(
    ctx: click.Context,
    fetch_all: bool,
    page_size: int | None,
    local_format: str | None,
) -> None:
    """List all users in the workspace."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = UsersAPI(settings)

    try:
        if fetch_all:
            results = api.list_all()
            click.echo(format_list(results, output_format))
        else:
            result = api.list(page_size=page_size)
            click.echo(format_output(result, output_format))
    finally:
        api.close()


@users.command("get")
@click.argument("user_id")
@FORMAT_OPTION
@click.pass_context
def get_user(
    ctx: click.Context, user_id: str, local_format: str | None
) -> None:
    """Retrieve a user by ID."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = UsersAPI(settings)
    try:
        result = api.retrieve(user_id)
        click.echo(format_output(result, output_format))
    finally:
        api.close()


@users.command("me")
@FORMAT_OPTION
@click.pass_context
def get_me(ctx: click.Context, local_format: str | None) -> None:
    """Get the bot user associated with the token."""
    settings = ctx.obj["settings"]
    output_format: OutputFormat = local_format or settings.output_format
    api = UsersAPI(settings)
    try:
        result = api.me()
        click.echo(format_output(result, output_format))
    finally:
        api.close()
