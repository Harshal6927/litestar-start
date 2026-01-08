"""Generator registry for framework and plugin discovery."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from litestar_start.core.base import BaseGenerator, PluginInterface


class GeneratorRegistry:
    """Central registry for discovering generators and plugins."""

    _backends: ClassVar[dict[str, type[BaseGenerator]]] = {}
    _frontends: ClassVar[dict[str, type[BaseGenerator]]] = {}
    _plugins: ClassVar[dict[str, dict[str, type[PluginInterface]]]] = {}

    @classmethod
    def register_backend(cls, generator: type[BaseGenerator]) -> None:
        """Register a backend generator.

        Args:
            generator: Backend generator class to register.

        """
        # Instantiate to get the name property
        instance = generator()
        cls._backends[instance.name] = generator

    @classmethod
    def register_frontend(cls, generator: type[BaseGenerator]) -> None:
        """Register a frontend generator.

        Args:
            generator: Frontend generator class to register.

        """
        # Instantiate to get the name property
        instance = generator()
        cls._frontends[instance.name] = generator

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
    def get_frontend(cls, name: str) -> type[BaseGenerator] | None:
        """Get a frontend generator by name.

        Args:
            name: Frontend generator name.

        Returns:
            Frontend generator class or None if not found.

        """
        return cls._frontends.get(name)

    @classmethod
    def list_backends(cls) -> list[str]:
        """List all registered backend names.

        Returns:
            List of backend generator names.

        """
        return list(cls._backends.keys())

    @classmethod
    def list_frontends(cls) -> list[str]:
        """List all registered frontend names.

        Returns:
            List of frontend generator names.

        """
        return list(cls._frontends.keys())

    @classmethod
    def register_plugin(cls, framework: str, plugin: type[PluginInterface]) -> None:
        """Register a plugin for a framework.

        Args:
            framework: Framework name (e.g., 'fastapi', 'litestar').
            plugin: Plugin class to register.

        """
        if framework not in cls._plugins:
            cls._plugins[framework] = {}
        # Instantiate to get the name property
        instance = plugin()
        cls._plugins[framework][instance.name] = plugin

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
            plugins = [p for p in plugins if p.category == category]

        return plugins

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
        cls._frontends.clear()
        cls._plugins.clear()
