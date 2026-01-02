"""CLI commands for cache management."""

from __future__ import annotations

import click

from notion_cli.client.cache import Cache
from notion_cli.output.formatters import format_output


@click.group()
def cache() -> None:
    """Manage the response cache."""
    pass


@cache.command("clear")
@click.option("--pattern", help="Pattern to match (currently clears all)")
@click.pass_context
def clear_cache(ctx: click.Context, pattern: str | None) -> None:
    """Clear cached responses."""
    settings = ctx.obj["settings"]
    cache_instance = Cache(
        cache_dir=settings.cache_dir,
        enabled=True,
    )

    try:
        count = cache_instance.invalidate(pattern)
        result = {
            "cleared": count,
            "cache_dir": str(settings.cache_dir),
        }
        click.echo(format_output(result, settings.output_format))
    finally:
        cache_instance.close()


@cache.command("info")
@click.pass_context
def cache_info(ctx: click.Context) -> None:
    """Show cache information."""
    settings = ctx.obj["settings"]
    cache_instance = Cache(
        cache_dir=settings.cache_dir,
        enabled=True,
    )

    try:
        result = {
            "cache_dir": str(settings.cache_dir),
            "entries": len(cache_instance.cache),
            "enabled": settings.use_cache,
            "default_ttl": settings.cache_ttl,
        }
        click.echo(format_output(result, settings.output_format))
    finally:
        cache_instance.close()
