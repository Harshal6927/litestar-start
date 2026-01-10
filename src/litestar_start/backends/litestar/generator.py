"""Litestar backend generator."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from litestar_start.backends.base import BackendGenerator
from litestar_start.core.templates import TemplateLoader
from litestar_start.core.utils import ensure_dir, write_file

if TYPE_CHECKING:
    from litestar_start.core.base import GeneratorContext


class LitestarGenerator(BackendGenerator):
    """Generator for Litestar backend projects."""

    def __init__(self) -> None:
        """Initialize the Litestar generator."""
        super().__init__()
        self.template_loader = TemplateLoader()
        # Register Litestar-specific templates
        self.template_loader.register_template_dir("litestar", Path(__file__).parent / "templates")

    @property
    def name(self) -> str:
        """Generator name."""
        return "litestar"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "Litestar"

    def get_dependencies(self) -> list[str]:
        """Get Litestar dependencies.

        Returns:
            List of package dependencies.

        """
        return [
            "litestar[standard]>=2.19.0",
            "python-dotenv>=1.2.1",
        ]

    def _generate_pyproject(self, backend_dir: Path, context: GeneratorContext) -> None:
        """Generate pyproject.toml for Litestar.

        Args:
            backend_dir: Backend directory path.
            context: Generator context.

        """
        template_context = {
            "project_slug": context.project_slug,
            "description": context.description,
            "dependencies": self.get_dependencies(),
        }
        content = self.template_loader.render("litestar:pyproject.toml.jinja", template_context)
        write_file(backend_dir / "pyproject.toml", content)

        # Create .python-version for uv
        write_file(backend_dir / ".python-version", "3.13\n")

        # Create .gitignore
        gitignore_content = self.template_loader.render("litestar:gitignore.jinja", {})
        write_file(backend_dir / ".gitignore", gitignore_content)

    def _generate_app_structure(self, backend_dir: Path, context: GeneratorContext) -> None:
        """Generate Litestar application structure.

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
        init_content = self.template_loader.render("litestar:app/__init__.py.jinja", {})
        write_file(app_dir / "__init__.py", init_content)

        # Create main.py
        main_content = self.template_loader.render("litestar:app/main.py.jinja", template_context)
        write_file(app_dir / "main.py", main_content)

        # Create config.py
        config_content = self.template_loader.render("litestar:app/config.py.jinja", template_context)
        write_file(app_dir / "config.py", config_content)

        # Create controllers directory
        controllers_dir = app_dir / "controllers"
        ensure_dir(controllers_dir)
        controllers_init_content = self.template_loader.render("litestar:controllers/__init__.py.jinja", {})
        write_file(controllers_dir / "__init__.py", controllers_init_content)

        # Create base controller
        controller_content = self.template_loader.render("litestar:controllers/base.py.jinja", {})
        write_file(controllers_dir / "base.py", controller_content)
