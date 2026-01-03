"""Markdown renderer for Notion blocks."""

from __future__ import annotations

from typing import Any


class MarkdownRenderer:
    """Converts Notion blocks to markdown."""

    def __init__(self) -> None:
        self._numbered_list_counters: dict[int, int] = {}
        self._last_block_type: str | None = None

    def render_blocks(self, blocks: list[dict[str, Any]]) -> str:
        """Render a list of blocks to markdown string."""
        if not blocks:
            return ""

        lines: list[str] = []
        for block in blocks:
            rendered = self.render_block(block, depth=0)
            if rendered:
                lines.append(rendered)

        return "\n".join(lines)

    def render_block(self, block: dict[str, Any], depth: int = 0) -> str:
        """Render a single block based on its type."""
        block_type = block.get("type", "")

        # Reset numbered list counter when block type changes
        if block_type != "numbered_list_item" and self._last_block_type == "numbered_list_item":
            self._numbered_list_counters = {}
        self._last_block_type = block_type

        # Dispatch to type-specific renderer
        handler = getattr(self, f"_render_{block_type}", None)
        if handler:
            result = handler(block, depth)
        else:
            result = self._render_unsupported(block, depth)

        # Handle nested children
        children = block.get("children", [])
        if children and block_type not in ("table", "column_list"):
            child_lines = []
            for child in children:
                child_rendered = self.render_block(child, depth + 1)
                if child_rendered:
                    child_lines.append(child_rendered)
            if child_lines:
                result += "\n".join(child_lines)
                if not result.endswith("\n"):
                    result += "\n"

        return result

    def render_rich_text(self, rich_text: list[dict[str, Any]]) -> str:
        """Convert Notion rich_text array to markdown string."""
        if not rich_text:
            return ""

        parts: list[str] = []
        for segment in rich_text:
            text = self._render_text_segment(segment)
            parts.append(text)

        return "".join(parts)

    def _render_text_segment(self, segment: dict[str, Any]) -> str:
        """Render a single rich text segment."""
        segment_type = segment.get("type", "text")

        if segment_type == "text":
            text_obj = segment.get("text", {})
            content = text_obj.get("content", "")
            link = text_obj.get("link")
            if link:
                url = link.get("url", "")
                content = f"[{content}]({url})"
        elif segment_type == "mention":
            content = self._render_mention(segment.get("mention", {}))
        elif segment_type == "equation":
            expression = segment.get("equation", {}).get("expression", "")
            return f"${expression}$"
        else:
            content = segment.get("plain_text", "")

        # Apply annotations
        annotations = segment.get("annotations", {})
        content = self._apply_annotations(content, annotations)

        # Handle href (external link on annotated text)
        href = segment.get("href")
        if href and not content.startswith("["):
            content = f"[{content}]({href})"

        return content

    def _render_mention(self, mention: dict[str, Any]) -> str:
        """Render a mention (user, page, date, etc.)."""
        mention_type = mention.get("type", "")

        if mention_type == "user":
            user = mention.get("user", {})
            name = user.get("name", "Unknown")
            return f"@{name}"
        elif mention_type == "page":
            page = mention.get("page", {})
            page_id = page.get("id", "")
            return f"[Page]({page_id})"
        elif mention_type == "database":
            db = mention.get("database", {})
            db_id = db.get("id", "")
            return f"[Database]({db_id})"
        elif mention_type == "date":
            date = mention.get("date", {})
            start = date.get("start", "")
            end = date.get("end")
            if end:
                return f"{start} → {end}"
            return start
        elif mention_type == "link_preview":
            url = mention.get("link_preview", {}).get("url", "")
            return f"[Link]({url})"

        return "[mention]"

    def _apply_annotations(self, text: str, annotations: dict[str, Any]) -> str:
        """Apply markdown formatting based on annotations."""
        if not text:
            return text

        # Order matters: innermost first
        if annotations.get("code"):
            text = f"`{text}`"
        if annotations.get("bold"):
            text = f"**{text}**"
        if annotations.get("italic"):
            text = f"*{text}*"
        if annotations.get("strikethrough"):
            text = f"~~{text}~~"
        if annotations.get("underline"):
            text = f"<u>{text}</u>"
        # Colors are dropped silently (no markdown equivalent)

        return text

    # Block type renderers

    def _render_paragraph(self, block: dict[str, Any], depth: int) -> str:
        """Render paragraph block."""
        content = block.get("paragraph", {})
        text = self.render_rich_text(content.get("rich_text", []))
        indent = "  " * depth if depth > 0 else ""
        return f"{indent}{text}\n"

    def _render_heading_1(self, block: dict[str, Any], depth: int) -> str:
        """Render heading 1 block."""
        content = block.get("heading_1", {})
        text = self.render_rich_text(content.get("rich_text", []))
        return f"# {text}\n"

    def _render_heading_2(self, block: dict[str, Any], depth: int) -> str:
        """Render heading 2 block."""
        content = block.get("heading_2", {})
        text = self.render_rich_text(content.get("rich_text", []))
        return f"## {text}\n"

    def _render_heading_3(self, block: dict[str, Any], depth: int) -> str:
        """Render heading 3 block."""
        content = block.get("heading_3", {})
        text = self.render_rich_text(content.get("rich_text", []))
        return f"### {text}\n"

    def _render_bulleted_list_item(self, block: dict[str, Any], depth: int) -> str:
        """Render bulleted list item."""
        content = block.get("bulleted_list_item", {})
        text = self.render_rich_text(content.get("rich_text", []))
        indent = "  " * depth
        return f"{indent}- {text}\n"

    def _render_numbered_list_item(self, block: dict[str, Any], depth: int) -> str:
        """Render numbered list item."""
        content = block.get("numbered_list_item", {})
        text = self.render_rich_text(content.get("rich_text", []))

        # Track counter per depth level
        if depth not in self._numbered_list_counters:
            self._numbered_list_counters[depth] = 0
        self._numbered_list_counters[depth] += 1
        # Reset deeper counters
        for d in list(self._numbered_list_counters.keys()):
            if d > depth:
                del self._numbered_list_counters[d]

        number = self._numbered_list_counters[depth]
        indent = "  " * depth
        return f"{indent}{number}. {text}\n"

    def _render_to_do(self, block: dict[str, Any], depth: int) -> str:
        """Render to-do item."""
        content = block.get("to_do", {})
        text = self.render_rich_text(content.get("rich_text", []))
        checked = content.get("checked", False)
        checkbox = "[x]" if checked else "[ ]"
        indent = "  " * depth
        return f"{indent}- {checkbox} {text}\n"

    def _render_code(self, block: dict[str, Any], depth: int) -> str:
        """Render code block."""
        content = block.get("code", {})
        text = self.render_rich_text(content.get("rich_text", []))
        language = content.get("language", "")
        indent = "  " * depth
        if indent:
            # Indent each line of code
            lines = text.split("\n")
            indented_code = "\n".join(f"{indent}{line}" for line in lines)
            return f"{indent}```{language}\n{indented_code}\n{indent}```\n"
        return f"```{language}\n{text}\n```\n"

    def _render_quote(self, block: dict[str, Any], depth: int) -> str:
        """Render quote block."""
        content = block.get("quote", {})
        text = self.render_rich_text(content.get("rich_text", []))
        indent = "  " * depth
        # Handle multi-line quotes
        lines = text.split("\n")
        quoted = "\n".join(f"{indent}> {line}" for line in lines)
        return f"{quoted}\n"

    def _render_callout(self, block: dict[str, Any], depth: int) -> str:
        """Render callout as blockquote with emoji."""
        content = block.get("callout", {})
        text = self.render_rich_text(content.get("rich_text", []))
        icon = content.get("icon", {})

        # Extract emoji or icon
        emoji = ""
        if icon.get("type") == "emoji":
            emoji = icon.get("emoji", "")
        elif icon.get("type") == "external":
            emoji = icon.get("external", {}).get("url", "")

        indent = "  " * depth
        if emoji:
            return f"{indent}> {emoji} {text}\n"
        return f"{indent}> {text}\n"

    def _render_divider(self, block: dict[str, Any], depth: int) -> str:
        """Render divider."""
        indent = "  " * depth
        return f"{indent}---\n"

    def _render_toggle(self, block: dict[str, Any], depth: int) -> str:
        """Render toggle as HTML details/summary."""
        content = block.get("toggle", {})
        text = self.render_rich_text(content.get("rich_text", []))
        indent = "  " * depth

        result = f"{indent}<details>\n{indent}<summary>{text}</summary>\n\n"

        # Children will be rendered by parent render_block
        # Just close the details tag after children are added
        children = block.get("children", [])
        if children:
            for child in children:
                child_rendered = self.render_block(child, depth + 1)
                if child_rendered:
                    result += child_rendered
            # Remove children so parent doesn't render them again
            block["children"] = []

        result += f"\n{indent}</details>\n"
        return result

    def _render_table(self, block: dict[str, Any], depth: int) -> str:
        """Render table."""
        children = block.get("children", [])
        if not children:
            return ""

        # Get column count from first row
        first_row = children[0].get("table_row", {}).get("cells", [])
        col_count = len(first_row)

        lines: list[str] = []
        indent = "  " * depth

        for i, row in enumerate(children):
            cells = row.get("table_row", {}).get("cells", [])
            cell_texts = [self.render_rich_text(cell) for cell in cells]
            # Pad if needed
            while len(cell_texts) < col_count:
                cell_texts.append("")
            lines.append(f"{indent}| " + " | ".join(cell_texts) + " |")

            # Add separator after header row
            if i == 0:
                lines.append(f"{indent}|" + "|".join(["---"] * col_count) + "|")

        return "\n".join(lines) + "\n"

    def _render_table_row(self, block: dict[str, Any], depth: int) -> str:
        """Table rows are handled by _render_table."""
        return ""

    def _render_column_list(self, block: dict[str, Any], depth: int) -> str:
        """Render column list - columns rendered sequentially."""
        children = block.get("children", [])
        if not children:
            return ""

        result = ""
        for i, column in enumerate(children):
            column_children = column.get("children", [])
            if column_children:
                result += f"<!-- Column {i + 1} -->\n"
                for child in column_children:
                    child_rendered = self.render_block(child, depth)
                    if child_rendered:
                        result += child_rendered
                result += "\n"

        return result

    def _render_column(self, block: dict[str, Any], depth: int) -> str:
        """Columns are handled by _render_column_list."""
        return ""

    def _render_image(self, block: dict[str, Any], depth: int) -> str:
        """Render image."""
        content = block.get("image", {})
        image_type = content.get("type", "")
        caption = self.render_rich_text(content.get("caption", []))

        if image_type == "external":
            url = content.get("external", {}).get("url", "")
        elif image_type == "file":
            url = content.get("file", {}).get("url", "")
        else:
            url = ""

        indent = "  " * depth
        if caption:
            return f"{indent}![{caption}]({url})\n"
        return f"{indent}![]({url})\n"

    def _render_video(self, block: dict[str, Any], depth: int) -> str:
        """Render video as link."""
        content = block.get("video", {})
        video_type = content.get("type", "")

        if video_type == "external":
            url = content.get("external", {}).get("url", "")
        elif video_type == "file":
            url = content.get("file", {}).get("url", "")
        else:
            url = ""

        indent = "  " * depth
        return f"{indent}[Video]({url})\n"

    def _render_file(self, block: dict[str, Any], depth: int) -> str:
        """Render file as link."""
        content = block.get("file", {})
        file_type = content.get("type", "")
        caption = self.render_rich_text(content.get("caption", []))
        name = content.get("name", "File")

        if file_type == "external":
            url = content.get("external", {}).get("url", "")
        elif file_type == "file":
            url = content.get("file", {}).get("url", "")
        else:
            url = ""

        indent = "  " * depth
        display = caption or name
        return f"{indent}[File: {display}]({url})\n"

    def _render_pdf(self, block: dict[str, Any], depth: int) -> str:
        """Render PDF as link."""
        content = block.get("pdf", {})
        pdf_type = content.get("type", "")
        caption = self.render_rich_text(content.get("caption", []))

        if pdf_type == "external":
            url = content.get("external", {}).get("url", "")
        elif pdf_type == "file":
            url = content.get("file", {}).get("url", "")
        else:
            url = ""

        indent = "  " * depth
        if caption:
            return f"{indent}[PDF: {caption}]({url})\n"
        return f"{indent}[PDF]({url})\n"

    def _render_bookmark(self, block: dict[str, Any], depth: int) -> str:
        """Render bookmark as link."""
        content = block.get("bookmark", {})
        url = content.get("url", "")
        caption = self.render_rich_text(content.get("caption", []))

        indent = "  " * depth
        if caption:
            return f"{indent}[{caption}]({url})\n"
        return f"{indent}[Bookmark]({url})\n"

    def _render_link_preview(self, block: dict[str, Any], depth: int) -> str:
        """Render link preview as link."""
        content = block.get("link_preview", {})
        url = content.get("url", "")

        indent = "  " * depth
        return f"{indent}[Link]({url})\n"

    def _render_embed(self, block: dict[str, Any], depth: int) -> str:
        """Render embed as link."""
        content = block.get("embed", {})
        url = content.get("url", "")
        caption = self.render_rich_text(content.get("caption", []))

        indent = "  " * depth
        if caption:
            return f"{indent}[Embed: {caption}]({url})\n"
        return f"{indent}[Embed]({url})\n"

    def _render_child_page(self, block: dict[str, Any], depth: int) -> str:
        """Render child page as link."""
        content = block.get("child_page", {})
        title = content.get("title", "Untitled")
        page_id = block.get("id", "")

        indent = "  " * depth
        return f"{indent}[Page: {title}]({page_id})\n"

    def _render_child_database(self, block: dict[str, Any], depth: int) -> str:
        """Render child database as link."""
        content = block.get("child_database", {})
        title = content.get("title", "Untitled")
        db_id = block.get("id", "")

        indent = "  " * depth
        return f"{indent}[Database: {title}]({db_id})\n"

    def _render_synced_block(self, block: dict[str, Any], depth: int) -> str:
        """Render synced block - just render children."""
        # Children will be handled by parent render_block
        return ""

    def _render_template(self, block: dict[str, Any], depth: int) -> str:
        """Render template block."""
        content = block.get("template", {})
        text = self.render_rich_text(content.get("rich_text", []))
        indent = "  " * depth
        return f"{indent}[Template: {text}]\n"

    def _render_link_to_page(self, block: dict[str, Any], depth: int) -> str:
        """Render link to page."""
        content = block.get("link_to_page", {})
        link_type = content.get("type", "")

        if link_type == "page_id":
            page_id = content.get("page_id", "")
            return f"[Page]({page_id})\n"
        elif link_type == "database_id":
            db_id = content.get("database_id", "")
            return f"[Database]({db_id})\n"

        return "[Link]\n"

    def _render_equation(self, block: dict[str, Any], depth: int) -> str:
        """Render equation block."""
        content = block.get("equation", {})
        expression = content.get("expression", "")
        indent = "  " * depth
        return f"{indent}$$\n{indent}{expression}\n{indent}$$\n"

    def _render_breadcrumb(self, block: dict[str, Any], depth: int) -> str:
        """Render breadcrumb - skip as it's navigational."""
        return ""

    def _render_table_of_contents(self, block: dict[str, Any], depth: int) -> str:
        """Render table of contents - skip as it's auto-generated."""
        return "[Table of Contents]\n"

    def _render_unsupported(self, block: dict[str, Any], depth: int) -> str:
        """Render unsupported block type."""
        block_type = block.get("type", "unknown")
        indent = "  " * depth
        return f"{indent}[unsupported: {block_type}]\n"
