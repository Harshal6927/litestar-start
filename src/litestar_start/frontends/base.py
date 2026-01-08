"""Base class for frontend generators."""

from __future__ import annotations

import shutil
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from litestar_start.core.base import BaseGenerator
from litestar_start.core.utils import ensure_dir, write_file

if TYPE_CHECKING:
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

        # Copy template files (Dockerfile, README, configs, etc.)
        self._copy_template_files(frontend_dir, context)

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

    def _copy_template_files(self, frontend_dir: Path, context: GeneratorContext) -> None:
        """Copy template files to frontend directory.

        Args:
            frontend_dir: Frontend directory path.
            context: Generator context.

        """
        templates_dir = Path(__file__).parent / "templates"

        # Copy Dockerfile
        if (templates_dir / "Dockerfile").exists():
            shutil.copy2(templates_dir / "Dockerfile", frontend_dir / "Dockerfile")

        # Copy nginx.conf
        if (templates_dir / "nginx.conf").exists():
            shutil.copy2(templates_dir / "nginx.conf", frontend_dir / "nginx.conf")

        # Copy .dockerignore
        if (templates_dir / ".dockerignore").exists():
            shutil.copy2(templates_dir / ".dockerignore", frontend_dir / ".dockerignore")

        # Copy .gitignore
        if (templates_dir / ".gitignore").exists():
            shutil.copy2(templates_dir / ".gitignore", frontend_dir / ".gitignore")

        # Copy .eslintrc.json
        if (templates_dir / ".eslintrc.json").exists():
            shutil.copy2(templates_dir / ".eslintrc.json", frontend_dir / ".eslintrc.json")

        # Copy .prettierrc
        if (templates_dir / ".prettierrc").exists():
            shutil.copy2(templates_dir / ".prettierrc", frontend_dir / ".prettierrc")

        # Copy .env.example (with templating)
        if (templates_dir / ".env.example").exists():
            env_template = (templates_dir / ".env.example").read_text()
            env_content = env_template.replace("{{ project_name }}", context.project_name)
            write_file(frontend_dir / ".env.example", env_content)

        # Copy README (with templating)
        if (templates_dir / "README.md").exists():
            readme_template = (templates_dir / "README.md").read_text()
            readme_content = readme_template.replace("{{ project_name }}", context.project_name)
            readme_content = readme_content.replace("{{ project_slug }}", context.project_slug)
            readme_content = readme_content.replace("{{ description }}", context.description or "")
            write_file(frontend_dir / "README.md", readme_content)
