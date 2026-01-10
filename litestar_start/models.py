"""Data models for project configuration."""

from enum import Enum

import msgspec


class Framework(str, Enum):
    """Supported backend frameworks."""

    LITESTAR = "Litestar"


class Database(str, Enum):
    """Supported database options."""

    POSTGRESQL = "PostgreSQL"
    SQLITE = "SQLite"
    MYSQL = "MySQL"
    NONE = "None"


class Plugin(str, Enum):
    """Available plugins."""

    SQLALCHEMY = "SQLAlchemy"
    JWT = "JWT"


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
    def has_sqlalchemy(self) -> bool:
        """Check if SQLAlchemy plugin is enabled."""
        return Plugin.SQLALCHEMY in self.plugins

    @property
    def has_jwt(self) -> bool:
        """Check if JWT plugin is enabled."""
        return Plugin.JWT in self.plugins

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
    def for_database(cls, db: Database) -> "DatabaseConfig | None":
        """Get configuration for a specific database."""
        configs = {
            Database.POSTGRESQL: cls(
                driver="postgresql+asyncpg",
                port=5432,
                default_url="postgresql+asyncpg://myuser:mypassword@localhost:5432/mydb",
                docker_image="postgres:17-alpine",
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
                docker_image="mysql:8.0",
            ),
        }
        return configs.get(db)
