"""FastAPI backend generator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from litestar_start.backends.base import BackendGenerator
from litestar_start.core.utils import ensure_dir, write_file

if TYPE_CHECKING:
    from pathlib import Path

    from litestar_start.core.base import GeneratorContext


class FastAPIGenerator(BackendGenerator):
    """Generator for FastAPI backend projects."""

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
            "pydantic>=2.5.0",
            "pydantic-settings>=2.1.0",
        ]

    def _generate_pyproject(self, backend_dir: Path, context: GeneratorContext) -> None:
        """Generate pyproject.toml for FastAPI.

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
        """Generate FastAPI application structure.

        Args:
            backend_dir: Backend directory path.
            context: Generator context.

        """
        app_dir = backend_dir / "app"
        ensure_dir(app_dir)

        # Create __init__.py
        write_file(app_dir / "__init__.py", '"""FastAPI application package."""\n')

        # Create main.py
        main_content = self._create_main_file(context)
        write_file(app_dir / "main.py", main_content)

        # Create config.py
        config_content = self._create_config_file(context)
        write_file(app_dir / "config.py", config_content)

        # Create api directory
        api_dir = app_dir / "api"
        ensure_dir(api_dir)
        write_file(api_dir / "__init__.py", '"""API routes package."""\n')

        # Create routes.py
        routes_content = self._create_routes_file()
        write_file(api_dir / "routes.py", routes_content)

    @staticmethod
    def _create_main_file(context: GeneratorContext) -> str:
        """Create main.py content.

        Args:
            context: Generator context.

        Returns:
            Main.py file content.

        """
        return f'''"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings

app = FastAPI(
    title="{context.project_name}",
    description="{context.description}",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {{"message": "Welcome to {context.project_name}!"}}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {{"status": "healthy"}}
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

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    APP_NAME: str = "{context.project_slug}"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"


settings = Settings()
'''

    @staticmethod
    def _create_routes_file() -> str:
        """Create routes.py content.

        Returns:
            Routes.py file content.

        """
        return '''"""API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")


@router.get("/status")
async def get_status() -> dict[str, str]:
    """Get API status."""
    return {"status": "ok", "version": "1.0.0"}
'''
