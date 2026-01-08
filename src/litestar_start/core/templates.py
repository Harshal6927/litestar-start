"""Template loading and rendering system."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from jinja2 import Environment, FileSystemLoader, PrefixLoader

if TYPE_CHECKING:
    from jinja2 import Template


class TemplateRenderError(Exception):
    """Raised when template rendering fails."""

    def __init__(self, template_name: str, original_error: Exception, context: dict[str, Any]) -> None:
        """Initialize error with context.

        Args:
            template_name: Name of the template that failed.
            original_error: The original exception.
            context: The context that was provided.

        """
        self.template_name = template_name
        self.original_error = original_error
        self.context = context

        message = f"""
Template rendering failed: {template_name}

Error: {original_error}

Available context keys: {list(context.keys())}

Tip: Check that all required variables are provided in the context.
"""
        super().__init__(message)


class TemplateValidator:
    """Validates template context before rendering."""

    REQUIRED_CONTEXT: ClassVar[dict[str, list[str]]] = {
        "base:gitignore.jinja": [],
        "fastapi:app/main.py.jinja": ["project_name", "description"],
        "fastapi:pyproject.toml.jinja": ["project_slug", "dependencies"],
        "litestar:app/main.py.jinja": ["project_name", "description"],
        "litestar:pyproject.toml.jinja": ["project_slug", "dependencies"],
    }

    @classmethod
    def validate(cls, template_name: str, context: dict[str, Any]) -> list[str]:
        """Validate context has required keys. Returns list of errors.

        Args:
            template_name: Name of the template to validate.
            context: Context dictionary to validate.

        Returns:
            List of validation error messages.

        """
        required = cls.REQUIRED_CONTEXT.get(template_name, [])
        return [f"Missing required context key: {key}" for key in required if key not in context]


class TemplateLoader:
    """Discovers and loads templates from multiple locations."""

    def __init__(self) -> None:
        """Initialize the template loader."""
        self._base_path = Path(__file__).parent / "templates" / "base"
        self._env: Environment | None = None
        self._loaders: dict[str, FileSystemLoader] = {}

    def register_template_dir(self, prefix: str, path: Path) -> None:
        """Register a template directory with a prefix.

        Args:
            prefix: Prefix for template names (e.g., "fastapi", "litestar").
            path: Path to the template directory.

        """
        if path.exists():
            self._loaders[prefix] = FileSystemLoader(str(path))
            self._env = None  # Reset environment to pick up new loader

    def _build_environment(self) -> Environment:
        """Build Jinja environment with all registered loaders.

        Returns:
            Configured Jinja2 Environment.

        """
        loaders: dict[str, FileSystemLoader] = {
            "base": FileSystemLoader(str(self._base_path)),
            **self._loaders,
        }

        env = Environment(
            loader=PrefixLoader(loaders, delimiter=":"),
            autoescape=False,  # We're generating code, not HTML
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters and globals
        env.filters.update(self._get_custom_filters())
        env.globals.update(self._get_custom_globals())

        return env

    @property
    def env(self) -> Environment:
        """Get or create the Jinja environment.

        Returns:
            The Jinja2 Environment instance.

        """
        if self._env is None:
            self._env = self._build_environment()
        return self._env

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of the template (e.g., "fastapi:app/main.py.jinja").
            context: Context dictionary for template rendering.

        Returns:
            Rendered template string.

        Raises:
            ValueError: If template context validation fails.
            TemplateRenderError: If template rendering fails.

        """
        # Validate context
        validation_errors = TemplateValidator.validate(template_name, context)
        if validation_errors:
            msg = f"Template context validation failed: {', '.join(validation_errors)}"
            raise ValueError(msg)

        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise TemplateRenderError(template_name, e, context) from e

    @staticmethod
    def _get_custom_filters() -> dict[str, Any]:
        """Get custom Jinja filters for code generation.

        Returns:
            Dictionary of custom filters.

        """
        return {
            "snake_case": lambda s: s.lower().replace("-", "_").replace(" ", "_"),
            "pascal_case": lambda s: "".join(w.title() for w in s.replace("-", "_").split("_")),
            "kebab_case": lambda s: s.lower().replace("_", "-").replace(" ", "-"),
            "quote": lambda s: f'"{s}"',
            "indent": lambda s, n: "\n".join(" " * n + line for line in s.split("\n")),
        }

    @staticmethod
    def _get_custom_globals() -> dict[str, Any]:
        """Get custom Jinja globals.

        Returns:
            Dictionary of custom globals.

        """
        return {
            "now": lambda: datetime.datetime.now(tz=datetime.timezone.utc),
            "year": lambda: datetime.datetime.now(tz=datetime.timezone.utc).year,
        }


class CachedTemplateLoader(TemplateLoader):
    """Template loader with caching for production."""

    def __init__(self, cache_size: int = 128) -> None:
        """Initialize cached template loader.

        Args:
            cache_size: Maximum number of compiled templates to cache.

        """
        super().__init__()
        self._cache_size = cache_size
        self._template_cache: dict[str, Template] = {}

    def _get_compiled_template(self, template_name: str) -> Template:
        """Get compiled template from cache or compile it.

        Args:
            template_name: Name of the template.

        Returns:
            Compiled Jinja2 template.

        """
        if template_name not in self._template_cache:
            self._template_cache[template_name] = self.env.get_template(template_name)
        return self._template_cache[template_name]

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with caching.

        Args:
            template_name: Name of the template.
            context: Context dictionary for rendering.

        Returns:
            Rendered template string.

        Raises:
            ValueError: If template context validation fails.
            TemplateRenderError: If template rendering fails.

        """
        # Validate context
        validation_errors = TemplateValidator.validate(template_name, context)
        if validation_errors:
            msg = f"Template context validation failed: {', '.join(validation_errors)}"
            raise ValueError(msg)

        try:
            template = self._get_compiled_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise TemplateRenderError(template_name, e, context) from e

    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._template_cache.clear()
