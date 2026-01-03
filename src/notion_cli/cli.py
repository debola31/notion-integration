"""Main CLI entry point for Notion CLI."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from notion_cli import __version__
from notion_cli.commands.blocks import blocks
from notion_cli.commands.cache import cache
from notion_cli.commands.comments import comments
from notion_cli.commands.databases import databases
from notion_cli.commands.pages import pages
from notion_cli.commands.search import search
from notion_cli.commands.users import users
from notion_cli.config import OutputFormat, Settings, set_settings
from notion_cli.output.errors import handle_error


@click.group()
@click.option(
    "--token", "-t",
    envvar="NOTION_INTEGRATION_TOKEN",
    help="Notion API token (or set NOTION_INTEGRATION_TOKEN env var)",
)
@click.option(
    "--format", "-f", "output_format",
    type=click.Choice(["json", "pretty", "compact", "markdown"]),
    default="json",
    help="Output format",
)
@click.option(
    "--no-cache",
    is_flag=True,
    help="Bypass cache for this request",
)
@click.option(
    "--cache-dir",
    type=click.Path(path_type=Path),
    help="Cache directory (default: ~/.cache/notion-cli)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
@click.version_option(version=__version__, prog_name="notion")
@click.pass_context
def main(
    ctx: click.Context,
    token: str | None,
    output_format: OutputFormat,
    no_cache: bool,
    cache_dir: Path | None,
    debug: bool,
) -> None:
    """Notion CLI - Full Notion API access for Claude Code agents.

    A production-ready CLI tool providing complete Notion API coverage with
    caching, rate limiting, and retry logic.

    \b
    Examples:
        notion pages get abc123
        notion search "meeting notes"
        notion databases query def456 --filter '{"property": "Status"}'

    \b
    Environment Variables:
        NOTION_INTEGRATION_TOKEN - Notion API integration token
    """
    # Configure logging
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    # Build settings
    settings = Settings(
        token=token,
        output_format=output_format,
        use_cache=not no_cache,
        debug=debug,
    )
    if cache_dir:
        settings.cache_dir = cache_dir

    # Store in context
    ctx.ensure_object(dict)
    ctx.obj["settings"] = settings
    set_settings(settings)


# Register command groups
main.add_command(pages)
main.add_command(databases)
main.add_command(blocks)
main.add_command(users)
main.add_command(search)
main.add_command(comments)
main.add_command(cache)


def cli() -> None:
    """CLI entry point with error handling."""
    try:
        main(obj={})
    except Exception as e:
        # Get output format from context if available
        output_format: OutputFormat = "json"
        handle_error(e, output_format)


if __name__ == "__main__":
    cli()
