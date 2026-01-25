"""Plugin system for project generation."""

import importlib
import pkgutil
import re
from pathlib import Path
from typing import Protocol, runtime_checkable

from src.models import ProjectConfig


def camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case.

    Returns:
        The converted string in snake_case.

    """
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


@runtime_checkable
class Plugin(Protocol):
    """Protocol for Litestar-Start plugins."""

    @property
    def id(self) -> str:
        """Unique identifier for the plugin (usually the directory name)."""
        ...

    @property
    def name(self) -> str:
        """Display name for the CLI."""
        ...

    @property
    def description(self) -> str:
        """Short description for the CLI."""
        ...

    @property
    def path(self) -> Path:
        """Absolute path to the plugin directory."""
        ...

    def is_applicable(self, config: ProjectConfig) -> bool:
        """Check if the plugin is applicable for the given configuration."""
        ...

    def get_template_context(self, config: ProjectConfig) -> dict:
        """Return context variables to be added to the template rendering context."""
        ...

    def post_generate(self, config: ProjectConfig, output_dir: Path) -> None:
        """Run post-generation logic."""
        ...


class BasePlugin:
    """Base class for plugins with default implementations."""

    path: Path

    @property
    def id(self) -> str:
        """Unique identifier for the plugin."""
        return camel_to_snake(self.__class__.__name__.replace("Plugin", ""))

    @property
    def description(self) -> str:
        """Short description for the CLI."""
        return ""

    def is_applicable(self, config: ProjectConfig) -> bool:  # noqa: ARG002, PLR6301
        """Default implementation: always applicable.

        Returns:
            True if the plugin is applicable for the given configuration.

        """
        return True

    def get_template_context(self, config: ProjectConfig) -> dict:  # noqa: ARG002, PLR6301
        """Default implementation: no extra context.

        Returns:
            An empty context dictionary.

        """
        return {}

    def post_generate(self, config: ProjectConfig, output_dir: Path) -> None:
        """Default implementation: no-op."""


def discover_plugins(framework: str) -> list[Plugin]:
    """Discover plugins for a specific framework.

    Args:
        framework: The framework name (e.g., 'Litestar').

    Returns:
        A list of discovered plugin instances.

    """
    from src.utils import get_package_dir

    plugins_path = get_package_dir() / framework / "Plugins"
    if not plugins_path.exists():
        return []

    plugins = []
    # Use pkgutil to iterate over modules in the Plugins directory
    for _, module_name, is_pkg in pkgutil.iter_modules([str(plugins_path)]):
        if is_pkg:
            try:
                module = importlib.import_module(f"src.{framework}.Plugins.{module_name}")
                # Look for a class that implements the Plugin protocol
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                        plugin_instance = attr()
                        plugin_instance.path = plugins_path / module_name
                        plugins.append(plugin_instance)
                        break  # Only one plugin per module
            except (ImportError, AttributeError):
                continue

    return plugins
