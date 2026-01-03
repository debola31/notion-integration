"""Unit tests for markdown renderer."""

from __future__ import annotations

import pytest

from notion_cli.output.markdown import MarkdownRenderer


class TestMarkdownRenderer:
    """Tests for MarkdownRenderer class."""

    @pytest.fixture
    def renderer(self) -> MarkdownRenderer:
        """Create a renderer instance."""
        return MarkdownRenderer()

    # Rich text tests

    def test_render_plain_text(self, renderer: MarkdownRenderer) -> None:
        """Test rendering plain text."""
        rich_text = [{"type": "text", "text": {"content": "Hello, world!"}}]
        assert renderer.render_rich_text(rich_text) == "Hello, world!"

    def test_render_empty_rich_text(self, renderer: MarkdownRenderer) -> None:
        """Test rendering empty rich text."""
        assert renderer.render_rich_text([]) == ""

    def test_render_bold_text(self, renderer: MarkdownRenderer) -> None:
        """Test rendering bold text."""
        rich_text = [{
            "type": "text",
            "text": {"content": "bold"},
            "annotations": {"bold": True}
        }]
        assert renderer.render_rich_text(rich_text) == "**bold**"

    def test_render_italic_text(self, renderer: MarkdownRenderer) -> None:
        """Test rendering italic text."""
        rich_text = [{
            "type": "text",
            "text": {"content": "italic"},
            "annotations": {"italic": True}
        }]
        assert renderer.render_rich_text(rich_text) == "*italic*"

    def test_render_code_text(self, renderer: MarkdownRenderer) -> None:
        """Test rendering inline code."""
        rich_text = [{
            "type": "text",
            "text": {"content": "code"},
            "annotations": {"code": True}
        }]
        assert renderer.render_rich_text(rich_text) == "`code`"

    def test_render_strikethrough_text(self, renderer: MarkdownRenderer) -> None:
        """Test rendering strikethrough text."""
        rich_text = [{
            "type": "text",
            "text": {"content": "deleted"},
            "annotations": {"strikethrough": True}
        }]
        assert renderer.render_rich_text(rich_text) == "~~deleted~~"

    def test_render_underline_text(self, renderer: MarkdownRenderer) -> None:
        """Test rendering underlined text (HTML fallback)."""
        rich_text = [{
            "type": "text",
            "text": {"content": "underlined"},
            "annotations": {"underline": True}
        }]
        assert renderer.render_rich_text(rich_text) == "<u>underlined</u>"

    def test_render_link(self, renderer: MarkdownRenderer) -> None:
        """Test rendering link."""
        rich_text = [{
            "type": "text",
            "text": {"content": "click here", "link": {"url": "https://example.com"}},
        }]
        assert renderer.render_rich_text(rich_text) == "[click here](https://example.com)"

    def test_render_nested_annotations(self, renderer: MarkdownRenderer) -> None:
        """Test rendering text with multiple annotations."""
        rich_text = [{
            "type": "text",
            "text": {"content": "important"},
            "annotations": {"bold": True, "italic": True}
        }]
        # Bold wraps italic
        assert renderer.render_rich_text(rich_text) == "***important***"

    def test_render_user_mention(self, renderer: MarkdownRenderer) -> None:
        """Test rendering user mention."""
        rich_text = [{
            "type": "mention",
            "mention": {
                "type": "user",
                "user": {"name": "John Doe", "id": "user-123"}
            }
        }]
        assert renderer.render_rich_text(rich_text) == "@John Doe"

    def test_render_date_mention(self, renderer: MarkdownRenderer) -> None:
        """Test rendering date mention."""
        rich_text = [{
            "type": "mention",
            "mention": {
                "type": "date",
                "date": {"start": "2024-01-15"}
            }
        }]
        assert renderer.render_rich_text(rich_text) == "2024-01-15"

    def test_render_date_range_mention(self, renderer: MarkdownRenderer) -> None:
        """Test rendering date range mention."""
        rich_text = [{
            "type": "mention",
            "mention": {
                "type": "date",
                "date": {"start": "2024-01-15", "end": "2024-01-20"}
            }
        }]
        assert renderer.render_rich_text(rich_text) == "2024-01-15 → 2024-01-20"

    def test_render_equation(self, renderer: MarkdownRenderer) -> None:
        """Test rendering inline equation."""
        rich_text = [{
            "type": "equation",
            "equation": {"expression": "E = mc^2"}
        }]
        assert renderer.render_rich_text(rich_text) == "$E = mc^2$"

    # Block type tests

    def test_render_paragraph(self, renderer: MarkdownRenderer) -> None:
        """Test rendering paragraph block."""
        block = {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "Hello, world!"}}]
            }
        }
        assert renderer.render_block(block) == "Hello, world!\n"

    def test_render_heading_1(self, renderer: MarkdownRenderer) -> None:
        """Test rendering heading 1."""
        block = {
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"type": "text", "text": {"content": "Title"}}]
            }
        }
        assert renderer.render_block(block) == "# Title\n"

    def test_render_heading_2(self, renderer: MarkdownRenderer) -> None:
        """Test rendering heading 2."""
        block = {
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Subtitle"}}]
            }
        }
        assert renderer.render_block(block) == "## Subtitle\n"

    def test_render_heading_3(self, renderer: MarkdownRenderer) -> None:
        """Test rendering heading 3."""
        block = {
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{"type": "text", "text": {"content": "Section"}}]
            }
        }
        assert renderer.render_block(block) == "### Section\n"

    def test_render_bulleted_list_item(self, renderer: MarkdownRenderer) -> None:
        """Test rendering bulleted list item."""
        block = {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Item"}}]
            }
        }
        assert renderer.render_block(block) == "- Item\n"

    def test_render_numbered_list_item(self, renderer: MarkdownRenderer) -> None:
        """Test rendering numbered list item."""
        block = {
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "First"}}]
            }
        }
        assert renderer.render_block(block) == "1. First\n"

    def test_render_multiple_numbered_list_items(self, renderer: MarkdownRenderer) -> None:
        """Test rendering multiple numbered list items."""
        blocks = [
            {
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "First"}}]
                }
            },
            {
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Second"}}]
                }
            },
            {
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Third"}}]
                }
            }
        ]
        result = renderer.render_blocks(blocks)
        assert "1. First" in result
        assert "2. Second" in result
        assert "3. Third" in result

    def test_render_to_do_unchecked(self, renderer: MarkdownRenderer) -> None:
        """Test rendering unchecked to-do item."""
        block = {
            "type": "to_do",
            "to_do": {
                "checked": False,
                "rich_text": [{"type": "text", "text": {"content": "Task"}}]
            }
        }
        assert renderer.render_block(block) == "- [ ] Task\n"

    def test_render_to_do_checked(self, renderer: MarkdownRenderer) -> None:
        """Test rendering checked to-do item."""
        block = {
            "type": "to_do",
            "to_do": {
                "checked": True,
                "rich_text": [{"type": "text", "text": {"content": "Done"}}]
            }
        }
        assert renderer.render_block(block) == "- [x] Done\n"

    def test_render_code_block(self, renderer: MarkdownRenderer) -> None:
        """Test rendering code block."""
        block = {
            "type": "code",
            "code": {
                "language": "python",
                "rich_text": [{"type": "text", "text": {"content": "print('hello')"}}]
            }
        }
        result = renderer.render_block(block)
        assert "```python" in result
        assert "print('hello')" in result
        assert result.endswith("```\n")

    def test_render_quote(self, renderer: MarkdownRenderer) -> None:
        """Test rendering quote block."""
        block = {
            "type": "quote",
            "quote": {
                "rich_text": [{"type": "text", "text": {"content": "Famous quote"}}]
            }
        }
        assert renderer.render_block(block) == "> Famous quote\n"

    def test_render_callout(self, renderer: MarkdownRenderer) -> None:
        """Test rendering callout block."""
        block = {
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "💡"},
                "rich_text": [{"type": "text", "text": {"content": "Tip"}}]
            }
        }
        assert renderer.render_block(block) == "> 💡 Tip\n"

    def test_render_divider(self, renderer: MarkdownRenderer) -> None:
        """Test rendering divider."""
        block = {"type": "divider", "divider": {}}
        assert renderer.render_block(block) == "---\n"

    def test_render_image_external(self, renderer: MarkdownRenderer) -> None:
        """Test rendering external image."""
        block = {
            "type": "image",
            "image": {
                "type": "external",
                "external": {"url": "https://example.com/img.png"},
                "caption": []
            }
        }
        assert renderer.render_block(block) == "![](https://example.com/img.png)\n"

    def test_render_image_with_caption(self, renderer: MarkdownRenderer) -> None:
        """Test rendering image with caption."""
        block = {
            "type": "image",
            "image": {
                "type": "external",
                "external": {"url": "https://example.com/img.png"},
                "caption": [{"type": "text", "text": {"content": "My image"}}]
            }
        }
        assert renderer.render_block(block) == "![My image](https://example.com/img.png)\n"

    def test_render_bookmark(self, renderer: MarkdownRenderer) -> None:
        """Test rendering bookmark."""
        block = {
            "type": "bookmark",
            "bookmark": {
                "url": "https://example.com",
                "caption": [{"type": "text", "text": {"content": "Example Site"}}]
            }
        }
        assert renderer.render_block(block) == "[Example Site](https://example.com)\n"

    def test_render_child_page(self, renderer: MarkdownRenderer) -> None:
        """Test rendering child page."""
        block = {
            "type": "child_page",
            "id": "page-123",
            "child_page": {"title": "Sub Page"}
        }
        assert renderer.render_block(block) == "[Page: Sub Page](page-123)\n"

    def test_render_child_database(self, renderer: MarkdownRenderer) -> None:
        """Test rendering child database."""
        block = {
            "type": "child_database",
            "id": "db-456",
            "child_database": {"title": "My Database"}
        }
        assert renderer.render_block(block) == "[Database: My Database](db-456)\n"

    def test_render_unsupported_block(self, renderer: MarkdownRenderer) -> None:
        """Test rendering unsupported block type."""
        block = {"type": "unknown_type", "unknown_type": {}}
        assert renderer.render_block(block) == "[unsupported: unknown_type]\n"

    # Nested block tests

    def test_render_nested_bulleted_list(self, renderer: MarkdownRenderer) -> None:
        """Test rendering nested bulleted list."""
        blocks = [{
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Parent"}}]
            },
            "children": [{
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Child"}}]
                }
            }]
        }]
        result = renderer.render_blocks(blocks)
        assert "- Parent" in result
        assert "  - Child" in result

    def test_render_deeply_nested_list(self, renderer: MarkdownRenderer) -> None:
        """Test rendering deeply nested list (3 levels)."""
        blocks = [{
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": "Level 1"}}]
            },
            "children": [{
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Level 2"}}]
                },
                "children": [{
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": "Level 3"}}]
                    }
                }]
            }]
        }]
        result = renderer.render_blocks(blocks)
        assert "- Level 1" in result
        assert "  - Level 2" in result
        assert "    - Level 3" in result

    # Table tests

    def test_render_table(self, renderer: MarkdownRenderer) -> None:
        """Test rendering table."""
        block = {
            "type": "table",
            "table": {"table_width": 2},
            "children": [
                {
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": "Header 1"}}],
                            [{"type": "text", "text": {"content": "Header 2"}}]
                        ]
                    }
                },
                {
                    "type": "table_row",
                    "table_row": {
                        "cells": [
                            [{"type": "text", "text": {"content": "Cell 1"}}],
                            [{"type": "text", "text": {"content": "Cell 2"}}]
                        ]
                    }
                }
            ]
        }
        result = renderer.render_block(block)
        assert "| Header 1 | Header 2 |" in result
        assert "|---|---|" in result
        assert "| Cell 1 | Cell 2 |" in result

    # Edge cases

    def test_render_empty_blocks(self, renderer: MarkdownRenderer) -> None:
        """Test rendering empty blocks list."""
        assert renderer.render_blocks([]) == ""

    def test_render_single_block(self, renderer: MarkdownRenderer) -> None:
        """Test rendering single block."""
        blocks = [{
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "Single"}}]
            }
        }]
        assert renderer.render_blocks(blocks) == "Single\n"

    def test_render_block_with_empty_rich_text(self, renderer: MarkdownRenderer) -> None:
        """Test rendering block with no text content."""
        block = {
            "type": "paragraph",
            "paragraph": {"rich_text": []}
        }
        assert renderer.render_block(block) == "\n"

    def test_render_toggle(self, renderer: MarkdownRenderer) -> None:
        """Test rendering toggle block."""
        block = {
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": "Click to expand"}}]
            },
            "children": [{
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "Hidden content"}}]
                }
            }]
        }
        result = renderer.render_block(block)
        assert "<details>" in result
        assert "<summary>Click to expand</summary>" in result
        assert "Hidden content" in result
        assert "</details>" in result
