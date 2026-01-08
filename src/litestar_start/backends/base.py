"""Base class for backend generators."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from litestar_start.core.base import BaseGenerator
from litestar_start.core.utils import ensure_dir

if TYPE_CHECKING:
    from pathlib import Path

    from litestar_start.core.base import GeneratorContext


class BackendGenerator(BaseGenerator):
    """Abstract base class for backend generators."""

    def generate(self, context: GeneratorContext) -> None:
        """Generate backend code.

        Args:
            context: Generator context.

        """
        backend_dir = context.output_dir / "backend"
        ensure_dir(backend_dir)

        # Generate pyproject.toml
        self._generate_pyproject(backend_dir, context)

        # Generate app structure
        self._generate_app_structure(backend_dir, context)

        # Apply plugins
        self._apply_plugins(backend_dir, context)

    @abstractmethod
    def _generate_pyproject(self, backend_dir: Path, context: GeneratorContext) -> None:
        """Generate pyproject.toml for the backend.

        Args:
            backend_dir: Backend directory path.
            context: Generator context.

        """
        ...

    @abstractmethod
    def _generate_app_structure(self, backend_dir: Path, context: GeneratorContext) -> None:
        """Generate the application structure.

        Args:
            backend_dir: Backend directory path.
            context: Generator context.

        """
        ...

    def _apply_plugins(self, backend_dir: Path, context: GeneratorContext) -> None:
        """Apply plugins to enhance the backend.

        Args:
            backend_dir: Backend directory path.
            context: Generator context.

        """
        # Plugin application will be implemented when plugins are created

    @staticmethod
    def _create_pyproject_content(
        project_name: str,
        dependencies: list[str],
        dev_dependencies: list[str] | None = None,
    ) -> str:
        """Create pyproject.toml content.

        Args:
            project_name: Project name.
            dependencies: List of dependencies.
            dev_dependencies: Optional list of dev dependencies.

        Returns:
            Pyproject.toml content as string.

        """
        dev_dependencies = dev_dependencies or ["pytest>=8.0.0", "pytest-cov>=4.1.0", "ruff>=0.1.0"]

        deps_str = "\n".join(f'    "{dep}",' for dep in dependencies)
        dev_deps_str = "\n".join(f'    "{dep}",' for dep in dev_dependencies)

        return f"""[project]
name = "{project_name}-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
{deps_str}
]

[project.optional-dependencies]
dev = [
{dev_deps_str}
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = []

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
"""
