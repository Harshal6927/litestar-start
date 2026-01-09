"""Register all generators with the registry."""

from litestar_start.backends.fastapi import FastAPIGenerator
from litestar_start.backends.litestar import LitestarGenerator
from litestar_start.generators.registry import GeneratorRegistry


def register_all_generators() -> None:
    """Register all available generators."""
    # Register backends
    GeneratorRegistry.register_backend(FastAPIGenerator)
    GeneratorRegistry.register_backend(LitestarGenerator)
