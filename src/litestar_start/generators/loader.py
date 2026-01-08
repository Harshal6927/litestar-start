"""Register all generators with the registry."""

from litestar_start.backends.fastapi import FastAPIGenerator
from litestar_start.backends.litestar import LitestarGenerator
from litestar_start.frontends.react import ReactGenerator
from litestar_start.generators.registry import GeneratorRegistry


def register_all_generators() -> None:
    """Register all available generators."""
    # Register backends
    GeneratorRegistry.register_backend(FastAPIGenerator)
    GeneratorRegistry.register_backend(LitestarGenerator)

    # Register frontends
    GeneratorRegistry.register_frontend(ReactGenerator)

    # TODO: Register plugins when needed
    # from litestar_start.backends.fastapi.plugins.sqlalchemy import SQLAlchemyPlugin
    # GeneratorRegistry.register_plugin("fastapi", SQLAlchemyPlugin)
