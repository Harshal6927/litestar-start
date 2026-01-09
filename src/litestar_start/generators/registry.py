"""Generator registry for framework and plugin discovery."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from litestar_start.core.base import BaseGenerator, PluginInterface


class GeneratorRegistry:
    """Central registry for discovering generators and plugins."""

    _backends: ClassVar[dict[str, type[BaseGenerator]]] = {}
    _plugins: ClassVar[dict[str, dict[str, type[PluginInterface]]]] = defaultdict(dict)

    @classmethod
    def register_backend(cls, generator: type[BaseGenerator]) -> type[BaseGenerator]:
        """Register a backend generator. Can be used as decorator.

        Args:
            generator: Backend generator class to register.

        Returns:
            The same generator class (for decorator usage).

        """
        # Instantiate to get the name property
        instance = generator()
        cls._backends[instance.name] = generator
        return generator

    @classmethod
    def get_backend(cls, name: str) -> type[BaseGenerator] | None:
        """Get a backend generator by name.

        Args:
            name: Backend generator name.

        Returns:
            Backend generator class or None if not found.

        """
        return cls._backends.get(name)

    @classmethod
    def list_backends(cls) -> list[tuple[str, str]]:
        """List all registered backends with display names.

        Returns:
            List of (name, display_name) tuples for all backends.

        """
        return [(instance.name, instance.display_name) for instance in (gen() for gen in cls._backends.values())]

    @classmethod
    def register_plugin(cls, framework: str, plugin: type[PluginInterface]) -> type[PluginInterface]:
        """Register a plugin for a framework.

        Args:
            framework: Framework name (e.g., 'fastapi', 'litestar').
            plugin: Plugin class to register.

        Returns:
            The same plugin class (for decorator usage).

        """
        instance = plugin()
        cls._plugins[framework][instance.name] = plugin
        return plugin

    @classmethod
    def get_plugins_by_category(cls, framework: str, category: str) -> list[type[PluginInterface]]:
        """Get all plugins for a framework in a specific category.

        Args:
            framework: Framework name.
            category: Plugin category ('orm', 'auth', 'cache', etc.).

        Returns:
            List of plugin classes in the specified category.

        """
        return [plugin for plugin in cls._plugins.get(framework, {}).values() if plugin().category == category]

    @classmethod
    def get_plugins_for(cls, framework: str, category: str | None = None) -> list[type[PluginInterface]]:
        """Get all plugins for a framework, optionally filtered by category.

        Args:
            framework: Framework name.
            category: Optional category filter ('orm', 'auth', etc.).

        Returns:
            List of plugin classes matching the criteria.

        """
        framework_plugins = cls._plugins.get(framework, {})
        plugins = list(framework_plugins.values())

        if category:
            plugins = [p for p in plugins if p().category == category]

        return plugins

    @classmethod
    def list_plugins(cls, framework: str, category: str | None = None) -> list[tuple[str, str]]:
        """List plugins for a framework with display names.

        Args:
            framework: Framework name.
            category: Optional category filter.

        Returns:
            List of (name, display_name) tuples for plugins.

        """
        plugins = cls.get_plugins_for(framework, category)
        return [(p().name, p().display_name) for p in plugins]

    @classmethod
    def get_plugin(cls, framework: str, plugin_name: str) -> type[PluginInterface] | None:
        """Get a specific plugin for a framework.

        Args:
            framework: Framework name.
            plugin_name: Plugin name.

        Returns:
            Plugin class or None if not found.

        """
        return cls._plugins.get(framework, {}).get(plugin_name)

    @classmethod
    def clear(cls) -> None:
        """Clear all registrations. Primarily for testing."""
        cls._backends.clear()
        cls._plugins.clear()
