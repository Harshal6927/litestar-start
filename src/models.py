"""Data models for project configuration."""

from __future__ import annotations

from enum import StrEnum

import msgspec

from src.utils import slugify

__all__ = [
    "Database",
    "DatabaseConfig",
    "Framework",
    "MemoryStore",
    "MemoryStoreConfig",
    "ProjectConfig",
]


class Framework(StrEnum):
    """Supported backend frameworks."""

    LITESTAR = "Litestar"


class Database(StrEnum):
    """Supported database options."""

    POSTGRESQL = "PostgreSQL"
    SQLITE = "SQLite"
    MYSQL = "MySQL"
    NONE = "None"


class MemoryStore(StrEnum):
    """Supported memory store options."""

    REDIS = "Redis"
    VALKEY = "Valkey"
    NONE = "None"


class ProjectConfig(msgspec.Struct):
    """Configuration for a new project."""

    name: str
    framework: Framework
    database: Database
    memory_store: MemoryStore
    plugins: list[str]
    docker: bool
    docker_dev_infra: bool

    @property
    def slug(self) -> str:
        """Return project name as a valid Python package name."""
        return slugify(self.name)

    def has_plugin(self, plugin_id: str) -> bool:
        """Check if a plugin is enabled.

        Args:
            plugin_id: The ID of the plugin to check.

        Returns:
            True if the plugin is enabled, False otherwise.

        """
        return plugin_id in self.plugins

    @property
    def can_use_docker_dev_infra(self) -> bool:
        """Check if the selected configuration supports containerized dev infrastructure."""
        has_db = self.database in {Database.POSTGRESQL, Database.MYSQL}
        has_store = self.memory_store in {MemoryStore.REDIS, MemoryStore.VALKEY}
        return has_db or has_store

    @property
    def needs_docker_dev_infra(self) -> bool:
        """Check if docker-compose.dev-infra.yml should be generated."""
        return self.docker_dev_infra and self.can_use_docker_dev_infra


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
                docker_image="postgres:17.7-alpine3.23",
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
                docker_image="mysql:8.4.8-oraclelinux9",
            ),
        }
        return configs.get(db)


class MemoryStoreConfig(msgspec.Struct):
    """Memory store specific configuration."""

    driver: str
    port: int
    default_url: str
    docker_image: str | None = None

    @classmethod
    def for_store(cls, store: MemoryStore) -> MemoryStoreConfig | None:
        """Get configuration for a specific memory store.

        Args:
            store: The memory store type.

        Returns:
            The configuration for the specified memory store, or None if not found.

        """
        configs = {
            MemoryStore.REDIS: cls(
                driver="redis",
                port=6379,
                default_url="redis://localhost:6379/0",
                docker_image="redis:8.4.0-bookworm",
            ),
            MemoryStore.VALKEY: cls(
                driver="redis",
                port=6379,
                default_url="redis://localhost:6379/0",
                docker_image="valkey/valkey:7.2.11-alpine3.23",
            ),
        }
        return configs.get(store)
