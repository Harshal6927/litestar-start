"""Plugins for Litestar backend."""

from litestar_start.generators.registry import GeneratorRegistry

from .sqlalchemy import SQLAlchemyPlugin

# Register all plugins for Litestar
_plugins = [
    SQLAlchemyPlugin,
]

for plugin in _plugins:
    GeneratorRegistry.register_plugin("litestar", plugin)

__all__ = ["SQLAlchemyPlugin"]
