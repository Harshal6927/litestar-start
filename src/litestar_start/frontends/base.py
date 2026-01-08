"""Base class for frontend generators."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from litestar_start.core.base import BaseGenerator
from litestar_start.core.utils import ensure_dir

if TYPE_CHECKING:
    from pathlib import Path

    from litestar_start.core.base import GeneratorContext


class FrontendGenerator(BaseGenerator):
    """Abstract base class for frontend generators."""

    def generate(self, context: GeneratorContext) -> None:
        """Generate frontend code.

        Args:
            context: Generator context.

        """
        frontend_dir = context.output_dir / "frontend"
        ensure_dir(frontend_dir)

        # Generate package.json
        self._generate_package_json(frontend_dir, context)

        # Generate source structure
        self._generate_src_structure(frontend_dir, context)

        # Generate config files
        self._generate_config_files(frontend_dir, context)

    @abstractmethod
    def _generate_package_json(self, frontend_dir: Path, context: GeneratorContext) -> None:
        """Generate package.json for the frontend.

        Args:
            frontend_dir: Frontend directory path.
            context: Generator context.

        """
        ...

    @abstractmethod
    def _generate_src_structure(self, frontend_dir: Path, context: GeneratorContext) -> None:
        """Generate the source code structure.

        Args:
            frontend_dir: Frontend directory path.
            context: Generator context.

        """
        ...

    @abstractmethod
    def _generate_config_files(self, frontend_dir: Path, context: GeneratorContext) -> None:
        """Generate configuration files (vite.config.js, etc.).

        Args:
            frontend_dir: Frontend directory path.
            context: Generator context.

        """
        ...
