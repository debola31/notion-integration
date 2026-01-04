# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Notion CLI is a production-ready command-line tool providing full Notion API coverage, designed as a reliable replacement for the unstable MCP server. It's built for AI coding agents to read and manipulate Notion workspaces.

## Development Commands

```bash
# Install for development
pip install -e ".[dev]"

# Run all tests (requires pytest-cov)
pytest

# Run tests without coverage (if pytest-cov not installed)
pytest --override-ini="addopts=" -v

# Run a single test file
pytest tests/unit/test_markdown.py --override-ini="addopts=" -v

# Run a specific test
pytest tests/unit/test_markdown.py::TestMarkdownRenderer::test_render_paragraph --override-ini="addopts=" -v

# Lint
ruff check src tests

# Type check
mypy src

# Test the CLI directly
export NOTION_INTEGRATION_TOKEN="secret_xxxxx"
notion --help
notion search "" --filter page --all --quiet
notion blocks children <page-id> --recursive --format markdown
```

## Architecture

### Layer Structure

```
CLI Layer (Click)     → src/notion_cli/commands/*.py
                           ↓
Output Layer          → src/notion_cli/output/formatters.py, markdown.py
                           ↓
API Layer             → src/notion_cli/api/*.py
                           ↓
Client Layer          → src/notion_cli/client/base.py
                           (rate_limiter.py, cache.py)
```

### Key Design Patterns

**Settings Flow**: Global options (`--token`, `--format`) are set in `cli.py` and stored in `ctx.obj["settings"]`. Each command also accepts local `--format` that overrides global.

**Output Formats**: All commands support `json`, `pretty`, `compact`, `markdown`. The `format_output()` and `format_list()` functions in `formatters.py` route to appropriate formatters. Markdown rendering is handled by `MarkdownRenderer` class in `markdown.py`.

**API Client Pattern**: Each API module (pages.py, blocks.py, etc.) creates a `NotionClient` via settings, which handles:
- Rate limiting (token bucket, 3 req/sec)
- Disk-based caching (5 min TTL)
- Retry with exponential backoff (via tenacity)
- Structured error handling

### Adding a New Command

1. Create/edit command file in `src/notion_cli/commands/`
2. Add `FORMAT_OPTION` decorator for local `--format` support
3. Use `output_format: OutputFormat = local_format or settings.output_format`
4. Call `format_output()` or `format_list()` with the output_format
5. Register in `cli.py` if new command group

### Output Format Type

```python
OutputFormat = Literal["json", "pretty", "compact", "markdown"]
```

When adding markdown support to new data types, update `format_as_markdown()` in `formatters.py`.

## Key Files

- `src/notion_cli/cli.py` - Main entry point, global options, command registration
- `src/notion_cli/config.py` - Settings dataclass, OutputFormat type
- `src/notion_cli/output/markdown.py` - MarkdownRenderer for block→markdown conversion
- `src/notion_cli/output/formatters.py` - Output routing (JSON/markdown)
- `src/notion_cli/client/base.py` - NotionClient with rate limiting, caching, retries
- `src/notion_cli/exceptions.py` - Structured errors with exit codes

## Testing

Tests are in `tests/unit/`. The markdown renderer has comprehensive tests in `test_markdown.py` covering all block types and rich text annotations. When adding new block type support, add corresponding tests.
