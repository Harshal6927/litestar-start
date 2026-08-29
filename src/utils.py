"""Utility functions for project generation."""

import re
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

__all__ = [
    "get_container_engine",
    "get_package_dir",
    "get_template_env",
    "slugify",
    "validate_project_name",
    "write_file",
]

MAX_PROJECT_NAME_LENGTH = 50


def get_container_engine() -> str | None:
    """Detect available container engine (Docker or Podman).

    Returns:
        'docker' if docker executable is found in PATH,
        'podman' if podman executable is found in PATH,
        None if neither executable is installed.

    """
    if shutil.which("docker"):
        return "docker"
    if shutil.which("podman"):
        return "podman"
    return None


def get_package_dir() -> Path:
    """Get the package directory.

    Returns:
        The path to the package directory.

    """
    return Path(__file__).parent


def get_template_env(template_dir: Path) -> Environment:
    """Create a Jinja2 environment for the given template directory.

    Args:
        template_dir: The directory containing the templates.

    Returns:
        A configured Jinja2 environment.

    """
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(default=False),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def slugify(text: str) -> str:
    """Convert text to a valid Python package name.

    Args:
        text: The text to slugify.

    Returns:
        The slugified text.

    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and hyphens with underscores
    text = re.sub(r"[-\s]+", "_", text)
    # Remove any characters that aren't alphanumeric or underscores
    text = re.sub(r"[^a-z0-9_]", "", text)
    # Ensure it doesn't start with a number
    if text and text[0].isdigit():
        text = f"_{text}"
    return text


def validate_project_name(name: str) -> str | None:
    """Validate project name. Returns error message or None if valid.

    Args:
        name: The project name to validate.

    Returns:
        An error message if the name is invalid, otherwise None.

    """
    if not name:
        return "Project name cannot be empty"
    if len(name) > MAX_PROJECT_NAME_LENGTH:
        return f"Project name must be less than {MAX_PROJECT_NAME_LENGTH} characters"
    # Check if slugified name is valid
    slug = slugify(name)
    if not slug:
        return "Project name must contain at least one letter"
    return None


def write_file(path: Path, content: str) -> None:
    """Write content to a file, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
