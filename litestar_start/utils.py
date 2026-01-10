"""Utility functions for project generation."""

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

MIN_PROJECT_NAME_LENGTH = 1
MAX_PROJECT_NAME_LENGTH = 50


def get_package_dir() -> Path:
    """Get the package directory."""
    return Path(__file__).parent


def get_template_env(template_dir: Path) -> Environment:
    """Create a Jinja2 environment for the given template directory."""
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(default=False),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def slugify(text: str) -> str:
    """Convert text to a valid Python package name."""
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
    """Validate project name. Returns error message or None if valid."""
    if not name:
        return "Project name cannot be empty"
    if len(name) < MIN_PROJECT_NAME_LENGTH:
        return f"Project name must be at least {MIN_PROJECT_NAME_LENGTH} characters"
    if len(name) > MAX_PROJECT_NAME_LENGTH:
        return f"Project name must be less than {MAX_PROJECT_NAME_LENGTH} characters"
    # Check if slugified name is valid
    slug = slugify(name)
    if not slug:
        return "Project name must contain at least one letter"
    return None


def create_directory(path: Path) -> None:
    """Create a directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str) -> None:
    """Write content to a file, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_template(env: Environment, template_name: str, context: dict) -> str:
    """Render a Jinja2 template with the given context."""
    template = env.get_template(template_name)
    return template.render(**context)
