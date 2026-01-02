"""Error output formatting."""

from __future__ import annotations

import sys
from typing import NoReturn

import click

from notion_cli.config import OutputFormat
from notion_cli.exceptions import NotionCLIError
from notion_cli.output.formatters import format_error


def handle_error(
    error: Exception,
    output_format: OutputFormat = "json",
) -> NoReturn:
    """
    Handle an error by formatting it and exiting.

    Args:
        error: The exception to handle.
        output_format: Output format type.
    """
    click.echo(format_error(error, output_format), err=True)

    if isinstance(error, NotionCLIError):
        sys.exit(error.exit_code)
    else:
        sys.exit(1)
