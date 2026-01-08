"""SQLAlchemy plugin for FastAPI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from litestar_start.core.base import PluginInterface

if TYPE_CHECKING:
    from litestar_start.core.base import GeneratorContext


class SQLAlchemyPlugin(PluginInterface):
    """SQLAlchemy ORM integration for FastAPI."""

    @property
    def name(self) -> str:
        """Plugin name."""
        return "sqlalchemy"

    @property
    def category(self) -> str:
        """Plugin category."""
        return "orm"

    def apply(self, context: GeneratorContext, base_files: dict[str, str]) -> dict[str, str]:
        """Apply SQLAlchemy integration.

        Args:
            context: Generator context.
            base_files: Base files dictionary.

        Returns:
            Updated files dictionary.

        """
        # Add database module
        database_module = self._create_database_module()
        base_files["app/database.py"] = database_module

        # Add models module
        models_module = self._create_models_module()
        base_files["app/models/__init__.py"] = models_module

        # Update config.py to include database settings
        if "app/config.py" in base_files:
            base_files["app/config.py"] = self._update_config(base_files["app/config.py"])

        return base_files

    def get_dependencies(self) -> list[str]:
        """Get SQLAlchemy dependencies.

        Returns:
            List of dependencies.

        """
        return [
            "sqlalchemy>=2.0.0",
            "alembic>=1.13.0",
        ]

    @staticmethod
    def get_env_vars() -> dict[str, str]:
        """Get environment variables.

        Returns:
            Dictionary of environment variables.

        """
        return {
            "DATABASE_URL": "sqlite:///./app.db",
        }

    @staticmethod
    def _create_database_module() -> str:
        """Create database.py module content.

        Returns:
            Database module content.

        """
        return '''"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

    @staticmethod
    def _create_models_module() -> str:
        """Create models module content.

        Returns:
            Models module content.

        """
        return '''"""Database models."""

from app.database import Base

# Import your models here
# from app.models.user import User
'''

    @staticmethod
    def _update_config(config_content: str) -> str:
        """Update config file with database URL.

        Args:
            config_content: Original config content.

        Returns:
            Updated config content.

        """
        # Simple string replacement to update DATABASE_URL comment
        return config_content.replace(
            '    DATABASE_URL: str = "sqlite:///./app.db"',
            '    DATABASE_URL: str = "sqlite:///./app.db"  # Override via environment variable',
        )
