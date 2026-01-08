"""FastAPI backend generator."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from litestar_start.backends.base import BackendGenerator
from litestar_start.core.templates import TemplateLoader
from litestar_start.core.utils import ensure_dir, write_file

if TYPE_CHECKING:
    from litestar_start.core.base import GeneratorContext


class FastAPIGenerator(BackendGenerator):
    """Generator for FastAPI backend projects."""

    def __init__(self) -> None:
        """Initialize the FastAPI generator."""
        super().__init__()
        self.template_loader = TemplateLoader()
        # Register FastAPI-specific templates
        self.template_loader.register_template_dir("fastapi", Path(__file__).parent / "templates")

    @property
    def name(self) -> str:
        """Generator name."""
        return "fastapi"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "FastAPI"

    def get_dependencies(self) -> list[str]:
        """Get FastAPI dependencies.

        Returns:
            List of package dependencies.

        """
        return [
            "fastapi>=0.109.0",
            "uvicorn[standard]>=0.27.0",
            "python-dotenv>=1.0.0",
            "msgspec>=0.20.0",
        ]

    def _generate_pyproject(self, backend_dir: Path, context: GeneratorContext) -> None:
        """Generate pyproject.toml for FastAPI.

        Args:
            backend_dir: Backend directory path.
            context: Generator context.

        """
        template_context = {
            "project_slug": context.project_slug,
            "description": context.description,
            "dependencies": self.get_dependencies(),
        }
        content = self.template_loader.render("fastapi:pyproject.toml.jinja", template_context)
        write_file(backend_dir / "pyproject.toml", content)

        # Create .python-version for uv
        write_file(backend_dir / ".python-version", "3.12\n")

        # Create .gitignore
        gitignore_content = self.template_loader.render("fastapi:gitignore.jinja", {})
        write_file(backend_dir / ".gitignore", gitignore_content)

    def _generate_app_structure(self, backend_dir: Path, context: GeneratorContext) -> None:
        """Generate FastAPI application structure.

        Args:
            backend_dir: Backend directory path.
            context: Generator context.

        """
        app_dir = backend_dir / "app"
        ensure_dir(app_dir)

        template_context = {
            "project_name": context.project_name,
            "project_slug": context.project_slug,
            "description": context.description,
        }

        # Create __init__.py
        init_content = self.template_loader.render("fastapi:app/__init__.py.jinja", {})
        write_file(app_dir / "__init__.py", init_content)

        # Create main.py
        main_content = self.template_loader.render("fastapi:app/main.py.jinja", template_context)
        write_file(app_dir / "main.py", main_content)

        # Create config.py
        config_content = self.template_loader.render("fastapi:app/config.py.jinja", template_context)
        write_file(app_dir / "config.py", config_content)

        # Create api directory
        api_dir = app_dir / "api"
        ensure_dir(api_dir)
        api_init_content = self.template_loader.render("fastapi:api/__init__.py.jinja", {})
        write_file(api_dir / "__init__.py", api_init_content)

        # Create routes.py
        routes_content = self.template_loader.render("fastapi:api/routes.py.jinja", {})
        write_file(api_dir / "routes.py", routes_content)
