"""Base class for backend generators."""

from __future__ import annotations

import shutil
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from litestar_start.core.base import BaseGenerator
from litestar_start.core.utils import ensure_dir, write_file

if TYPE_CHECKING:
    from litestar_start.core.base import GeneratorContext


class BackendGenerator(BaseGenerator):
    """Abstract base class for backend generators."""

    def generate(self, context: GeneratorContext) -> None:
        """Generate backend code.

        Args:
            context: Generator context.

        """
        backend_dir = context.output_dir
        ensure_dir(backend_dir)

        # Generate pyproject.toml
        self._generate_pyproject(backend_dir, context)

        # Generate app structure
        self._generate_app_structure(backend_dir, context)

        # Copy template files (Dockerfile, README, etc.)
        self._copy_template_files(backend_dir, context)

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
    def _copy_template_files(backend_dir: Path, context: GeneratorContext) -> None:
        """Copy template files to backend directory.

        Args:
            backend_dir: Backend directory path.
            context: Generator context.

        """
        templates_dir = Path(__file__).parent / "templates"

        # Copy Dockerfile
        if (templates_dir / "Dockerfile").exists():
            shutil.copy2(templates_dir / "Dockerfile", backend_dir / "Dockerfile")

        # Copy .dockerignore
        if (templates_dir / ".dockerignore").exists():
            shutil.copy2(templates_dir / ".dockerignore", backend_dir / ".dockerignore")

        # Copy .gitignore
        if (templates_dir / ".gitignore").exists():
            shutil.copy2(templates_dir / ".gitignore", backend_dir / ".gitignore")

        # Copy README (with templating)
        if (templates_dir / "README.md").exists():
            readme_template = (templates_dir / "README.md").read_text()
            readme_content = readme_template.replace("{{ project_name }}", context.project_name)
            readme_content = readme_content.replace("{{ project_slug }}", context.project_slug)
            readme_content = readme_content.replace("{{ description }}", context.description or "")
            write_file(backend_dir / "README.md", readme_content)

        # Copy tests directory
        tests_template_dir = templates_dir / "tests"
        if tests_template_dir.exists():
            tests_dir = backend_dir / "tests"
            ensure_dir(tests_dir)
            for test_file in tests_template_dir.glob("*.py"):
                shutil.copy2(test_file, tests_dir / test_file.name)

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
        dev_dependencies = dev_dependencies or [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.23.0",
            "ruff>=0.4.0",
            "mypy>=1.9.0",
        ]

        deps_str = "\n".join(f'    "{dep}",' for dep in dependencies)
        dev_deps_str = "\n".join(f'    "{dep}",' for dep in dev_dependencies)

        return f"""[project]
name = "{project_name}-backend"
version = "0.1.0"
description = "Backend for {project_name}"
readme = "README.md"
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

[tool.uv]
dev-dependencies = [
{dev_deps_str}
]

[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
"""
