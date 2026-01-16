"""Data models for project configuration."""

from __future__ import annotations

from enum import StrEnum

import msgspec


class Framework(StrEnum):
    """Supported backend frameworks."""

    LITESTAR = "Litestar"


class Database(StrEnum):
    """Supported database options."""

    POSTGRESQL = "PostgreSQL"
    SQLITE = "SQLite"
    MYSQL = "MySQL"
    NONE = "None"


class Plugin(StrEnum):
    """Available plugins."""

    ADVANCED_ALCHEMY = "AdvancedAlchemy"
    LITESTAR_SAQ = "LitestarSAQ"
    LITESTAR_VITE = "LitestarVite"


class ProjectConfig(msgspec.Struct):
    """Configuration for a new project."""

    name: str
    framework: Framework
    database: Database
    plugins: list[Plugin]
    docker: bool
    docker_infra: bool

    @property
    def slug(self) -> str:
        """Return project name as a valid Python package name."""
        return self.name.lower().replace("-", "_").replace(" ", "_")

    @property
    def has_advanced_alchemy(self) -> bool:
        """Check if AdvancedAlchemy plugin is enabled."""
        return Plugin.ADVANCED_ALCHEMY in self.plugins

    @property
    def needs_docker_infra(self) -> bool:
        """Check if docker-compose.infra.yml should be generated."""
        return self.docker_infra and self.database in {Database.POSTGRESQL, Database.MYSQL}


class DatabaseConfig(msgspec.Struct):
    """Database-specific configuration."""

    driver: str
    port: int
    default_url: str
    docker_image: str | None = None

    @classmethod
    def for_database(cls, db: Database) -> DatabaseConfig | None:
        """Get configuration for a specific database.

        Args:
            db: The database type.

        Returns:
            The configuration for the specified database, or None if not found.

        """
        configs = {
            Database.POSTGRESQL: cls(
                driver="postgresql+psycopg",
                port=5432,
                default_url="postgresql+psycopg://myuser:mypassword@localhost:5432/mydb",
                docker_image="postgres:18.1",
            ),
            Database.SQLITE: cls(
                driver="sqlite+aiosqlite",
                port=0,
                default_url="sqlite+aiosqlite:///./app.db",
                docker_image=None,
            ),
            Database.MYSQL: cls(
                driver="mysql+asyncmy",
                port=3306,
                default_url="mysql+asyncmy://myuser:mypassword@localhost:3306/mydb",
                docker_image="mysql:lts-oraclelinux9",
            ),
        }
        return configs.get(db)
