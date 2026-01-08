"""Template rendering utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateRenderer:
    """Jinja2 template renderer."""

    def __init__(self, template_dir: Path | None = None) -> None:
        """Initialize template renderer.

        Args:
            template_dir: Directory containing templates. If None, uses package templates.

        """
        if template_dir is None:
            template_dir = self._get_default_template_dir()

        self.template_dir = template_dir
        self.env = self._create_env(template_dir)

    @staticmethod
    def _get_default_template_dir() -> Path:
        """Get the default templates directory.

        Returns:
            Path to templates directory.

        """
        package_dir = Path(__file__).parent.parent.parent.parent
        template_dir = package_dir / "templates"

        if not template_dir.exists():
            # Fallback for development
            template_dir = Path(__file__).parent.parent.parent.parent / "templates"

        return template_dir

    @staticmethod
    def _create_env(template_dir: Path) -> Environment:
        """Create Jinja2 environment.

        Args:
            template_dir: Directory containing templates.

        Returns:
            Configured Jinja2 Environment.

        """
        return Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_path: str, context: dict[str, Any]) -> str:
        """Render a template with the given context.

        Args:
            template_path: Path to template relative to template_dir.
            context: Template context variables.

        Returns:
            Rendered template content.

        """
        template = self.env.get_template(template_path)
        return template.render(**context)

    def render_string(self, template_string: str, context: dict[str, Any]) -> str:
        """Render a template string with the given context.

        Args:
            template_string: Template content as string.
            context: Template context variables.

        Returns:
            Rendered content.

        """
        template = self.env.from_string(template_string)
        return template.render(**context)
