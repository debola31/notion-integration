# Notion CLI

A production-ready CLI tool providing full Notion API coverage, designed for Claude Code agents to replace the unstable MCP server.

## Features

- **Full Notion API Coverage**: Pages, databases, blocks, users, search, and comments
- **Rate Limiting**: Automatic token bucket rate limiting (3 req/sec) with retry logic
- **Caching**: Disk-based caching with TTL for faster repeated queries
- **Retry Logic**: Exponential backoff for rate limits and server errors
- **JSON Output**: Machine-parseable output designed for AI agents
- **Error Handling**: Structured errors with exit codes for automation

## Installation

```bash
# Install with pip
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Or with uv
uv pip install -e .
```

## Quick Start

```bash
# Set your Notion integration token
export NOTION_INTEGRATION_TOKEN="secret_xxxxx"

# Test the connection
notion users me

# Search for pages
notion search "meeting notes"

# Get a page
notion pages get <page-id>
```

## Authentication

Create a Notion integration at https://www.notion.so/my-integrations and get your integration token.

```bash
export NOTION_INTEGRATION_TOKEN="secret_your_token_here"
```

Or pass it directly:

```bash
notion --token secret_xxxxx pages get <page-id>
```

## CLI Commands

### Pages

```bash
# Get a page
notion pages get <page-id>

# Create a page
notion pages create --parent-id <parent-page-id> --title "My Page"
notion pages create --parent-id <database-id> --parent-type database --title "Database Item"

# Update a page
notion pages update <page-id> --properties '{"Status": {"select": {"name": "Done"}}}'

# Archive/restore a page
notion pages archive <page-id>
notion pages restore <page-id>

# Get a page property
notion pages property <page-id> <property-id>
```

### Databases

```bash
# Get a database
notion databases get <database-id>

# Query a database
notion databases query <database-id>
notion databases query <database-id> --filter '{"property": "Status", "select": {"equals": "Done"}}'
notion databases query <database-id> --sort '[{"property": "Created", "direction": "descending"}]'
notion databases query <database-id> --all  # Get all results (handles pagination)

# Create a database
notion databases create --parent-id <page-id> --title "Tasks" --properties '{"Name": {"title": {}}, "Status": {"select": {"options": []}}}'

# Update a database
notion databases update <database-id> --title "New Title"
```

### Blocks

```bash
# Get a block
notion blocks get <block-id>

# Get block children
notion blocks children <block-id>
notion blocks children <block-id> --recursive  # Get all nested children

# Append children to a block
notion blocks append <block-id> --content '[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}]'

# Update a block
notion blocks update <block-id> --content '{"paragraph": {"rich_text": [{"text": {"content": "Updated"}}]}}'

# Delete a block
notion blocks delete <block-id>
```

### Users

```bash
# List all users
notion users list
notion users list --all  # Get all users (handles pagination)

# Get a user
notion users get <user-id>

# Get the bot user (current integration)
notion users me
```

### Search

```bash
# Search for everything
notion search "query"

# Filter by type
notion search "query" --filter page
notion search "query" --filter database

# Sort by last edited
notion search "query" --sort descending

# Get all results
notion search "query" --all
```

### Comments

```bash
# List comments on a page/block
notion comments list --block-id <block-id>
notion comments list --block-id <block-id> --all

# Create a comment
notion comments create --page-id <page-id> --text "This is a comment"
notion comments create --page-id <page-id> --text "Reply" --discussion-id <discussion-id>
```

### Cache

```bash
# Clear all cached responses
notion cache clear

# Show cache info
notion cache info
```

## Global Options

```
--token, -t       Notion API token (or set NOTION_INTEGRATION_TOKEN)
--format, -f      Output format: json (default), pretty, compact
--no-cache        Bypass cache for this request
--cache-dir       Custom cache directory
--debug           Enable debug logging
--version         Show version
--help            Show help
```

## Output Format

All commands output JSON with a consistent structure:

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "cached": false,
    "timestamp": "2024-01-02T12:00:00Z"
  }
}
```

### Error Response

```json
{
  "error": true,
  "code": "not_found",
  "message": "Page not found",
  "details": { ... }
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Authentication error |
| 3 | Not found |
| 4 | Validation error |
| 5 | Rate limit exceeded |
| 6 | Permission denied |
| 7 | Server error |
| 8 | Network error |

## Python Library Usage

You can also use this as a Python library:

```python
from notion_cli.config import Settings
from notion_cli.api import PagesAPI, DatabasesAPI, SearchAPI

# Create settings
settings = Settings(token="secret_xxxxx")

# Use the APIs
pages = PagesAPI(settings)
page = pages.retrieve("page-id")
print(page)
pages.close()

# Search
search = SearchAPI(settings)
results = search.search_all("meeting notes")
print(results)
search.close()
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov

# Lint
ruff check src tests

# Type check
mypy src
```

## Project Structure

```
notion-integration/
├── src/notion_cli/
│   ├── api/           # Notion API clients
│   ├── client/        # HTTP client, cache, rate limiter
│   ├── commands/      # CLI command groups
│   ├── output/        # Output formatters
│   ├── cli.py         # Main CLI entry point
│   ├── config.py      # Configuration
│   └── exceptions.py  # Custom exceptions
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
└── pyproject.toml     # Project configuration
```

## License

MIT License - see LICENSE file for details.
