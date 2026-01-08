"""Shared utility functions."""

from __future__ import annotations

from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists.

    Returns:
        The directory path.

    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def slugify(text: str) -> str:
    """Convert text to a slug-friendly format.

    Args:
        text: Text to slugify.

    Returns:
        Slugified text.

    """
    return text.lower().replace(" ", "-").replace("_", "-")


def write_file(path: Path, content: str) -> None:
    """Write content to a file, creating parent directories if needed.

    Args:
        path: File path to write to.
        content: Content to write.

    """
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
