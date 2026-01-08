"""File merging strategies for plugin content combination.

This module handles merging content from multiple plugins when they modify
the same file.
"""

from __future__ import annotations

import ast
import json
from copy import deepcopy
from enum import StrEnum


class MergeMode(StrEnum):
    """Merge mode for handling file conflicts."""

    CREATE = "create"  # Fail if file exists
    REPLACE = "replace"  # Overwrite entire file
    APPEND = "append"  # Add content at end
    PREPEND = "prepend"  # Add content at start
    MERGE = "merge"  # Smart merge (for Python/JSON)


class FileMerger:
    """Handle merging content from multiple plugins."""

    @staticmethod
    def merge_python_imports(existing: str, new_imports: list[str]) -> str:
        """Add imports to a Python file without duplicates.

        Args:
            existing: Existing Python file content.
            new_imports: List of import statements to add.

        Returns:
            Updated Python file content with merged imports.

        """
        try:
            tree = ast.parse(existing)
        except SyntaxError:
            # If we can't parse, just append imports
            return existing + "\n" + "\n".join(new_imports)

        # Extract existing imports
        existing_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                existing_imports.update(f"import {alias.name}" for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                existing_imports.update(f"from {module} import {alias.name}" for alias in node.names)

        # Filter out duplicates
        new_unique_imports = [imp for imp in new_imports if imp not in existing_imports]

        if not new_unique_imports:
            return existing

        # Find position to insert (after existing imports, before other code)
        lines = existing.splitlines()
        insert_pos = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("#")
                and not stripped.startswith("import")
                and not stripped.startswith("from")
            ):
                insert_pos = i
                break
        else:
            insert_pos = len(lines)

        # Insert new imports
        updated_lines = lines[:insert_pos] + new_unique_imports + [""] + lines[insert_pos:]
        return "\n".join(updated_lines)

    @staticmethod
    def merge_python_code(existing: str, new_code: str, marker: str) -> str:
        """Insert code at a marked location in Python file.

        Args:
            existing: Existing Python file content.
            new_code: New code to insert.
            marker: Comment marker to find insertion point (e.g., "# {{ plugins }}").

        Returns:
            Updated Python file content with inserted code.

        """
        lines = existing.splitlines()
        for i, line in enumerate(lines):
            if marker in line:
                # Insert new code after the marker
                indent = len(line) - len(line.lstrip())
                indented_code = "\n".join(" " * indent + ln for ln in new_code.splitlines())
                lines[i] = indented_code
                break

        return "\n".join(lines)

    @staticmethod
    def merge_json(existing: dict, new_data: dict) -> dict:
        """Deep merge two JSON/dict structures.

        Args:
            existing: Existing dictionary.
            new_data: New data to merge in.

        Returns:
            Merged dictionary.

        """
        result = deepcopy(existing)
        for key, value in new_data.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = FileMerger.merge_json(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                # For lists, extend (avoid duplicates)
                result[key] = list(set(result[key] + value))
            else:
                result[key] = value
        return result

    @staticmethod
    def merge_toml(existing: str, new_content: str) -> str:
        """Merge TOML content.

        Args:
            existing: Existing TOML content.
            new_content: New TOML content to merge.

        Returns:
            Merged TOML content.

        Note:
            This is a simple implementation. For production, use a TOML library.

        """
        # For now, just append new content
        # TODO: Implement proper TOML merging with a library like tomli/tomli_w
        return existing + "\n\n" + new_content

    @staticmethod
    def apply_merge(
        mode: MergeMode | str,
        existing_content: str | None,
        new_content: str,
    ) -> str:
        """Apply merge strategy to content.

        Args:
            mode: Merge mode to use.
            existing_content: Existing file content (None if file doesn't exist).
            new_content: New content to merge.

        Returns:
            Merged content.

        Raises:
            ValueError: If mode is CREATE and file already exists.

        """
        if isinstance(mode, str):
            mode = MergeMode(mode)

        if mode == MergeMode.CREATE:
            if existing_content is not None:
                raise ValueError("File already exists and mode is CREATE")
            return new_content

        if mode == MergeMode.REPLACE:
            return new_content

        if existing_content is None:
            # No existing content, just use new content
            return new_content

        if mode == MergeMode.APPEND:
            return existing_content + "\n\n" + new_content

        if mode == MergeMode.PREPEND:
            return new_content + "\n\n" + existing_content

        if mode == MergeMode.MERGE:
            # Try to detect file type and merge appropriately
            if new_content.strip().startswith("{"):
                # JSON-like
                try:
                    existing_dict = json.loads(existing_content)
                    new_dict = json.loads(new_content)
                    merged = FileMerger.merge_json(existing_dict, new_dict)
                    return json.dumps(merged, indent=2)
                except json.JSONDecodeError:
                    pass

            # Default to append for merge mode
            return existing_content + "\n\n" + new_content

        return new_content
