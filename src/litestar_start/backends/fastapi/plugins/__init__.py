"""Plugins for FastAPI backend."""

from litestar_start.generators.registry import GeneratorRegistry

from .sqlalchemy import SQLAlchemyPlugin

# Register all plugins for FastAPI
_plugins = [
    SQLAlchemyPlugin,
]

for plugin in _plugins:
    GeneratorRegistry.register_plugin("fastapi", plugin)

__all__ = ["SQLAlchemyPlugin"]
