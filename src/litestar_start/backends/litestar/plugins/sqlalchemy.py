"""SQLAlchemy plugin for Litestar."""

from __future__ import annotations

from typing import Any

from litestar_start.core.plugin import PluginFile, PluginInterface, PluginMetadata, PluginResult


class SQLAlchemyPlugin(PluginInterface):
    """SQLAlchemy ORM integration for Litestar using built-in plugin."""

    metadata = PluginMetadata(
        name="sqlalchemy",
        display_name="SQLAlchemy",
        category="orm",
        description="SQLAlchemy via Litestar's built-in SQLAlchemy plugin",
        requires=["database"],
    )

    def apply(self) -> PluginResult:
        """Apply SQLAlchemy integration for Litestar.

        Returns:
            PluginResult with files, dependencies, and environment variables.

        """
        database = self.context.config.get("database", "postgresql")

        # Litestar has different SQLAlchemy integration
        dependencies = [
            "litestar[sqlalchemy]",  # Uses Litestar's bundled plugin
            "alembic>=1.13.0",
        ]

        # Add async driver
        if database == "postgresql":
            dependencies.append("asyncpg>=0.29.0")
        elif database == "mysql":
            dependencies.append("aiomysql>=0.2.0")

        files = [
            PluginFile(
                path="app/db/plugin.py",
                content=self._create_plugin_config(),
            ),
            PluginFile(
                path="app/db/models.py",
                content=self._create_models_module(),
            ),
            PluginFile(
                path="app/main.py",
                content=self._create_main_with_db(),
                mode="replace",  # Replace the base main.py
            ),
            PluginFile(
                path="alembic.ini",
                content=self._create_alembic_ini(),
            ),
            PluginFile(
                path="alembic/env.py",
                content=self._create_alembic_env(),
            ),
        ]

        return PluginResult(
            files=files,
            dependencies=dependencies,
            env_vars={"DATABASE_URL": self._get_async_url(database)},
        )

    def _get_async_url(self, database: str) -> str:
        """Get async database URL template.

        Args:
            database: Database type.

        Returns:
            Async database URL template string.

        """
        # Litestar uses async drivers
        templates = {
            "postgresql": "postgresql+asyncpg://user:password@localhost:5432/{project_slug}",
            "mysql": "mysql+aiomysql://user:password@localhost:3306/{project_slug}",
            "sqlite": "sqlite+aiosqlite:///./app.db",
        }
        return templates.get(database, "").format(project_slug=self.context.project_slug)

    def get_template_context(self) -> dict[str, Any]:
        """Get template context for rendering.

        Returns:
            Dictionary with template variables.

        """
        return {
            "database": self.context.config.get("database"),
            "project_name": self.context.project_name,
        }

    @staticmethod
    def _create_plugin_config() -> str:
        """Create Litestar SQLAlchemy plugin configuration.

        Returns:
            Plugin configuration content.

        """
        return '''"""SQLAlchemy plugin configuration for Litestar."""

from advanced_alchemy.extensions.litestar import (
    AlembicAsyncConfig,
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    async_autocommit_before_send_handler,
)
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import settings


def get_sqlalchemy_config() -> SQLAlchemyAsyncConfig:
    """Get SQLAlchemy configuration for Litestar.

    Returns:
        SQLAlchemy configuration.

    """
    session_config = AsyncSessionConfig(expire_on_commit=False)

    return SQLAlchemyAsyncConfig(
        connection_string=settings.DATABASE_URL,
        session_config=session_config,
        before_send_handler=async_autocommit_before_send_handler,
    )


def get_alembic_config() -> AlembicAsyncConfig:
    """Get Alembic configuration for Litestar.

    Returns:
        Alembic configuration.

    """
    return AlembicAsyncConfig(
        config_file_path="alembic.ini",
        script_config="alembic/",
        version_table_name="alembic_version",
    )
'''

    @staticmethod
    def _create_models_module() -> str:
        """Create models module content.

        Returns:
            Models module content.

        """
        return '''"""Database models."""

from advanced_alchemy.base import UUIDAuditBase


class Base(UUIDAuditBase):
    """Base class for all database models."""

    __abstract__ = True


# Define your models here
# Example:
# class User(Base):
#     __tablename__ = "users"
#     name: Mapped[str]
#     email: Mapped[str]
'''

    def _create_main_with_db(self) -> str:
        """Create main.py with database integration.

        Returns:
            Main module content with database setup.

        """
        return '''"""Main application module."""

from litestar import Litestar
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyInitPlugin

from app.core.config import settings
from app.db.plugin import get_sqlalchemy_config


def create_app() -> Litestar:
    """Create and configure the Litestar application.

    Returns:
        Configured Litestar application.

    """
    sqlalchemy_config = get_sqlalchemy_config()

    return Litestar(
        route_handlers=[],
        debug=settings.DEBUG,
        plugins=[SQLAlchemyInitPlugin(config=sqlalchemy_config)],
    )


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
'''

    @staticmethod
    def _create_alembic_ini() -> str:
        """Create alembic.ini content.

        Returns:
            Alembic configuration content.

        """
        return """# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# timezone to use when rendering the date within the migration file
# as well as the filename.
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; this defaults
# to alembic/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path
# version_locations = %(here)s/bar %(here)s/bat alembic/versions

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = driver://user:pass@localhost/dbname


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

    @staticmethod
    def _create_alembic_env() -> str:
        """Create alembic env.py content for async SQLAlchemy.

        Returns:
            Alembic environment configuration.

        """
        return '''"""Alembic migration environment for async SQLAlchemy."""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import your models' Base
from app.db.models import Base
from app.core.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set SQLAlchemy URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with connection.

    Args:
        connection: Database connection.

    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
