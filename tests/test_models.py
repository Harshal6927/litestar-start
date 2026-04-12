# ruff: noqa: PLR6301
"""Unit tests for data models."""

from src.models import Database, DatabaseConfig, Framework, MemoryStore, MemoryStoreConfig, ProjectConfig

POSTGRESQL_PORT = 5432
MYSQL_PORT = 3306
REDIS_PORT = 6379


class TestProjectConfig:
    """Tests for ProjectConfig model."""

    def test_slug_lowercase(self) -> None:
        """Verify slug converts to lowercase."""
        config = ProjectConfig(
            name="MyProject",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert config.slug == "myproject"

    def test_slug_replace_hyphens(self) -> None:
        """Verify slug replaces hyphens with underscores."""
        config = ProjectConfig(
            name="my-project-name",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert config.slug == "my_project_name"

    def test_slug_replace_spaces(self) -> None:
        """Verify slug replaces spaces with underscores."""
        config = ProjectConfig(
            name="My Project Name",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert config.slug == "my_project_name"

    def test_slug_mixed_case_hyphens_spaces(self) -> None:
        """Verify slug handles mixed case, hyphens, and spaces."""
        config = ProjectConfig(
            name="My-Cool Project",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert config.slug == "my_cool_project"

    def test_has_plugin_present(self) -> None:
        """Verify has_plugin returns True when plugin is in list."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=["advanced_alchemy", "litestar_saq"],
            docker=False,
            docker_infra=False,
        )
        assert config.has_plugin("advanced_alchemy") is True
        assert config.has_plugin("litestar_saq") is True

    def test_has_plugin_absent(self) -> None:
        """Verify has_plugin returns False when plugin is not in list."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=["advanced_alchemy"],
            docker=False,
            docker_infra=False,
        )
        assert config.has_plugin("litestar_saq") is False
        assert config.has_plugin("nonexistent") is False

    def test_needs_docker_infra_false_when_docker_infra_disabled(self) -> None:
        """Verify needs_docker_infra is False when docker_infra flag is False."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.POSTGRESQL,
            memory_store=MemoryStore.REDIS,
            plugins=[],
            docker=False,
            docker_infra=False,  # Disabled
        )
        assert config.needs_docker_infra is False

    def test_needs_docker_infra_true_with_postgresql(self) -> None:
        """Verify needs_docker_infra is True with PostgreSQL."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.POSTGRESQL,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=True,
        )
        assert config.needs_docker_infra is True

    def test_needs_docker_infra_true_with_mysql(self) -> None:
        """Verify needs_docker_infra is True with MySQL."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.MYSQL,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=True,
        )
        assert config.needs_docker_infra is True

    def test_needs_docker_infra_false_with_sqlite(self) -> None:
        """Verify needs_docker_infra is False with SQLite."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.SQLITE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=True,
        )
        assert config.needs_docker_infra is False

    def test_needs_docker_infra_false_with_no_database(self) -> None:
        """Verify needs_docker_infra is False with no database."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=True,
        )
        assert config.needs_docker_infra is False

    def test_needs_docker_infra_true_with_redis(self) -> None:
        """Verify needs_docker_infra is True with Redis."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.REDIS,
            plugins=[],
            docker=False,
            docker_infra=True,
        )
        assert config.needs_docker_infra is True

    def test_needs_docker_infra_true_with_valkey(self) -> None:
        """Verify needs_docker_infra is True with Valkey."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.VALKEY,
            plugins=[],
            docker=False,
            docker_infra=True,
        )
        assert config.needs_docker_infra is True

    def test_needs_docker_infra_true_with_postgres_and_redis(self) -> None:
        """Verify needs_docker_infra is True with PostgreSQL and Redis."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.POSTGRESQL,
            memory_store=MemoryStore.REDIS,
            plugins=[],
            docker=False,
            docker_infra=True,
        )
        assert config.needs_docker_infra is True

    def test_slug_removes_special_characters(self) -> None:
        """Verify slug removes special characters like @, #, $."""
        config = ProjectConfig(
            name="my@project#name",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert config.slug == "myprojectname"

    def test_slug_handles_digit_prefix(self) -> None:
        """Verify slug adds underscore prefix for digit-starting names."""
        config = ProjectConfig(
            name="123app",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert config.slug == "_123app"

    def test_slug_handles_consecutive_separators(self) -> None:
        """Verify slug collapses consecutive hyphens/spaces to single underscore."""
        config = ProjectConfig(
            name="my--project  name",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert config.slug == "my_project_name"


class TestDatabaseConfig:
    """Tests for DatabaseConfig model."""

    def test_for_database_postgresql(self) -> None:
        """Verify for_database returns correct config for PostgreSQL."""
        config = DatabaseConfig.for_database(Database.POSTGRESQL)
        assert config is not None
        assert config.driver == "postgresql+psycopg"
        assert config.port == POSTGRESQL_PORT
        assert "postgresql+psycopg://" in config.default_url
        assert config.docker_image == "postgres:17.7-alpine3.23"

    def test_for_database_sqlite(self) -> None:
        """Verify for_database returns correct config for SQLite."""
        config = DatabaseConfig.for_database(Database.SQLITE)
        assert config is not None
        assert config.driver == "sqlite+aiosqlite"
        assert config.port == 0
        assert "sqlite+aiosqlite://" in config.default_url
        assert config.docker_image is None

    def test_for_database_mysql(self) -> None:
        """Verify for_database returns correct config for MySQL."""
        config = DatabaseConfig.for_database(Database.MYSQL)
        assert config is not None
        assert config.driver == "mysql+asyncmy"
        assert config.port == MYSQL_PORT
        assert "mysql+asyncmy://" in config.default_url
        assert config.docker_image == "mysql:8.4.8-oraclelinux9"

    def test_for_database_none(self) -> None:
        """Verify for_database returns None for Database.NONE."""
        config = DatabaseConfig.for_database(Database.NONE)
        assert config is None


class TestMemoryStoreConfig:
    """Tests for MemoryStoreConfig model."""

    def test_for_store_redis(self) -> None:
        """Verify for_store returns correct config for Redis."""
        config = MemoryStoreConfig.for_store(MemoryStore.REDIS)
        assert config is not None
        assert config.driver == "redis"
        assert config.port == REDIS_PORT
        assert "redis://" in config.default_url
        assert config.docker_image == "redis:8.4.0-bookworm"

    def test_for_store_valkey(self) -> None:
        """Verify for_store returns correct config for Valkey."""
        config = MemoryStoreConfig.for_store(MemoryStore.VALKEY)
        assert config is not None
        assert config.driver == "redis"
        assert config.port == REDIS_PORT
        assert "redis://" in config.default_url
        assert config.docker_image == "valkey/valkey:7.2.11-alpine3.23"

    def test_for_store_none(self) -> None:
        """Verify for_store returns None for MemoryStore.NONE."""
        config = MemoryStoreConfig.for_store(MemoryStore.NONE)
        assert config is None
