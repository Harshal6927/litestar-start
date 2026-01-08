"""Litestar backend generator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from litestar_start.backends.base import BackendGenerator
from litestar_start.core.utils import ensure_dir, write_file

if TYPE_CHECKING:
    from pathlib import Path

    from litestar_start.core.base import GeneratorContext


class LitestarGenerator(BackendGenerator):
    """Generator for Litestar backend projects."""

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
            "litestar>=2.5.0",
            "uvicorn[standard]>=0.27.0",
            "python-dotenv>=1.0.0",
        ]

    def _generate_pyproject(self, backend_dir: Path, context: GeneratorContext) -> None:
        """Generate pyproject.toml for Litestar.

        Args:
            backend_dir: Backend directory path.
            context: Generator context.

        """
        content = self._create_pyproject_content(
            context.project_slug,
            self.get_dependencies(),
        )
        write_file(backend_dir / "pyproject.toml", content)

        # Create .python-version for uv
        write_file(backend_dir / ".python-version", "3.12\n")

    def _generate_app_structure(self, backend_dir: Path, context: GeneratorContext) -> None:
        """Generate Litestar application structure.

        Args:
            backend_dir: Backend directory path.
            context: Generator context.

        """
        app_dir = backend_dir / "app"
        ensure_dir(app_dir)

        # Create __init__.py
        write_file(app_dir / "__init__.py", '"""Litestar application package."""\n')

        # Create main.py
        main_content = self._create_main_file(context)
        write_file(app_dir / "main.py", main_content)

        # Create config.py
        config_content = self._create_config_file(context)
        write_file(app_dir / "config.py", config_content)

        # Create controllers directory
        controllers_dir = app_dir / "controllers"
        ensure_dir(controllers_dir)
        write_file(controllers_dir / "__init__.py", '"""API controllers package."""\n')

        # Create base controller
        controller_content = self._create_controller_file()
        write_file(controllers_dir / "base.py", controller_content)

    @staticmethod
    def _create_main_file(context: GeneratorContext) -> str:
        """Create main.py content.

        Args:
            context: Generator context.

        Returns:
            Main.py file content.

        """
        return f'''"""Litestar application entry point."""

from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from litestar.contrib.pydantic import PydanticPlugin

from app.config import settings
from app.controllers.base import base_controller


@get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {{"message": "Welcome to {context.project_name}!"}}


@get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {{"status": "healthy"}}


app = Litestar(
    route_handlers=[root, health, base_controller],
    cors_config=CORSConfig(allow_origins=settings.ALLOWED_ORIGINS),
    plugins=[PydanticPlugin()],
    debug=settings.DEBUG,
)
'''

    @staticmethod
    def _create_config_file(context: GeneratorContext) -> str:
        """Create config.py content.

        Args:
            context: Generator context.

        Returns:
            Config.py file content.

        """
        return f'''"""Application configuration."""

from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application settings."""

    # Application
    APP_NAME: str = "{context.project_slug}"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: list[str] = field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"


settings = Settings()
'''

    @staticmethod
    def _create_controller_file() -> str:
        """Create base controller content.

        Returns:
            Controller file content.

        """
        return '''"""Base API controller."""

from litestar import Controller, get


class BaseController(Controller):
    """Base API controller."""

    path = "/api/v1"

    @get("/status")
    async def get_status(self) -> dict[str, str]:
        """Get API status."""
        return {"status": "ok", "version": "1.0.0"}


base_controller = BaseController
'''
