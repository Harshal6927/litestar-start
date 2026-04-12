from pathlib import Path

from pytest_mock import MockerFixture

from src.Litestar.generator import LitestarGenerator
from src.models import Database, Framework, MemoryStore, ProjectConfig

MYSQL_PORT = 3306


def test_litestar_generator_context(tmp_path: Path) -> None:
    """Verify Litestar generator template context values with plugins and database enabled."""
    config = ProjectConfig(
        name="Test Project",
        framework=Framework.LITESTAR,
        database=Database.SQLITE,
        memory_store=MemoryStore.NONE,
        plugins=["advanced_alchemy"],
        docker=True,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)
    context = generator._get_template_context()

    assert context["project_name"] == "Test Project"
    assert context["advanced_alchemy"] is True
    assert context["litestar_vite"] is False
    assert context["has_database"] is True
    assert context["docker"] is True


def test_litestar_generator_no_plugins(tmp_path: Path) -> None:
    """Verify Litestar generator template context values with no plugins or database."""
    config = ProjectConfig(
        name="Test Project",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=[],
        docker=False,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)
    context = generator._get_template_context()

    assert context["advanced_alchemy"] is False
    assert context["has_database"] is False


def test_litestar_generator_plugins_rendering(tmp_path: Path) -> None:
    """Verify that plugin templates are correctly rendered into the output directory."""
    config = ProjectConfig(
        name="Plugin Test",
        framework=Framework.LITESTAR,
        database=Database.POSTGRESQL,
        memory_store=MemoryStore.NONE,
        plugins=["advanced_alchemy"],
        docker=False,
        docker_infra=True,
    )

    generator = LitestarGenerator(config, tmp_path)
    generator.generate()

    # Verify base files
    assert (tmp_path / "pyproject.toml").exists()
    assert (tmp_path / "src" / "backend" / "app.py").exists()

    # Verify AdvancedAlchemy plugin files
    # These are in src/Litestar/Plugins/AdvancedAlchemy/Templates/
    # Should be rendered to src/backend of tmp_path
    assert (tmp_path / "src" / "backend" / "models" / "users.py").exists()
    assert (tmp_path / "src" / "backend" / "lib" / "dependencies.py").exists()
    assert (tmp_path / "src" / "backend" / "lib" / "services.py").exists()


def test_litestar_generator_memory_store_context(tmp_path: Path) -> None:
    """Verify Litestar generator template context values with memory store enabled."""
    config = ProjectConfig(
        name="Store Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.REDIS,
        plugins=[],
        docker=True,
        docker_infra=True,
    )

    generator = LitestarGenerator(config, tmp_path)
    context = generator._get_template_context()

    assert context["memory_store"] == MemoryStore.REDIS
    assert context["has_store"] is True
    assert context["store_config"].driver == "redis"
    assert context["store_config"].docker_image == "redis:8.4.0-bookworm"


def test_litestar_generator_docker_compose_rendering(tmp_path: Path) -> None:
    """Verify that docker-compose.yml is correctly rendered with dependencies."""
    config = ProjectConfig(
        name="Docker Test",
        framework=Framework.LITESTAR,
        database=Database.POSTGRESQL,
        memory_store=MemoryStore.REDIS,
        plugins=[],
        docker=True,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)
    generator.generate()

    docker_compose = tmp_path / "docker-compose.yml"
    assert docker_compose.exists()
    content = docker_compose.read_text()

    # Check env var
    assert "REDIS_URL=redis://docker_test_redis:6379/0" in content
    assert "DATABASE_URL=postgresql+psycopg://myuser:mypassword@postgres:5432/mydb" in content

    # Check depends_on structure
    assert "depends_on:" in content
    assert "postgres:" in content
    assert "redis:" in content

    # Check services
    assert "image: postgres:17.7-alpine3.23" in content
    assert "image: redis:8.4.0-bookworm" in content


def test_litestar_generator_saq_context(tmp_path: Path) -> None:
    """Verify Litestar generator template context values with SAQ plugin enabled."""
    config = ProjectConfig(
        name="SAQ Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.REDIS,
        plugins=["litestar_saq"],
        docker=False,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)
    context = generator._get_template_context()

    assert context["litestar_saq"] is True
    assert context["has_store"] is True
    assert context["memory_store"] == MemoryStore.REDIS


def test_litestar_generator_saq_rendering(tmp_path: Path) -> None:
    """Verify that SAQ plugin templates are correctly rendered into the output directory."""
    config = ProjectConfig(
        name="SAQ Plugin Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.REDIS,
        plugins=["litestar_saq"],
        docker=False,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)
    generator.generate()

    # Verify base files
    assert (tmp_path / "pyproject.toml").exists()
    assert (tmp_path / "src" / "backend" / "app.py").exists()
    assert (tmp_path / "src" / "backend" / "config.py").exists()

    # Verify SAQ plugin files
    assert (tmp_path / "src" / "backend" / "lib" / "tasks.py").exists()

    # Verify SAQ config in config.py
    config_content = (tmp_path / "src" / "backend" / "config.py").read_text()
    assert "from litestar_saq import CronJob, QueueConfig, SAQConfig, SAQPlugin" in config_content
    assert "saq = SAQPlugin(" in config_content
    assert 'QueueConfig(\n                name="default"' in config_content

    # Verify SAQ plugin in app.py
    app_content = (tmp_path / "src" / "backend" / "app.py").read_text()
    assert "from src.backend.config import saq" in app_content
    assert "saq" in app_content.lower(), "SAQ plugin reference not found in app.py"

    # Verify SAQ dependency in pyproject.toml
    pyproject_content = (tmp_path / "pyproject.toml").read_text()
    assert "litestar-saq>=0.7.0" in pyproject_content


def test_litestar_generator_granian_context(tmp_path: Path) -> None:
    """Verify Litestar generator template context values with Granian plugin enabled."""
    config = ProjectConfig(
        name="Granian Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=["litestar_granian"],
        docker=False,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)
    context = generator._get_template_context()

    assert context["litestar_granian"] is True


def test_litestar_generator_granian_rendering(tmp_path: Path) -> None:
    """Verify that Granian plugin templates are correctly rendered into the output directory."""
    config = ProjectConfig(
        name="Granian Plugin Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=["litestar_granian"],
        docker=False,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)
    generator.generate()

    # Verify base files
    assert (tmp_path / "pyproject.toml").exists()
    assert (tmp_path / "src" / "backend" / "app.py").exists()

    # Verify Granian plugin in app.py
    app_content = (tmp_path / "src" / "backend" / "app.py").read_text()
    assert "from litestar_granian import GranianPlugin" in app_content
    assert "GranianPlugin()," in app_content

    # Verify Granian dependency in pyproject.toml
    pyproject_content = (tmp_path / "pyproject.toml").read_text()
    assert "litestar-granian>=0.14.2" in pyproject_content


def test_litestar_generator_mysql_context(tmp_path: Path) -> None:
    """Verify Litestar generator template context values with MySQL database."""
    config = ProjectConfig(
        name="MySQL Test",
        framework=Framework.LITESTAR,
        database=Database.MYSQL,
        memory_store=MemoryStore.NONE,
        plugins=["advanced_alchemy"],
        docker=False,
        docker_infra=True,
    )

    generator = LitestarGenerator(config, tmp_path)
    context = generator._get_template_context()

    assert context["has_database"] is True
    assert context["database"] == Database.MYSQL
    assert context["db_config"].driver == "mysql+asyncmy"
    assert context["db_config"].port == MYSQL_PORT
    assert context["db_config"].docker_image == "mysql:8.4.8-oraclelinux9"


def test_litestar_generator_mysql_rendering(tmp_path: Path) -> None:
    """Verify that MySQL database is correctly rendered in docker-compose.infra.yml."""
    config = ProjectConfig(
        name="MySQL Test",
        framework=Framework.LITESTAR,
        database=Database.MYSQL,
        memory_store=MemoryStore.NONE,
        plugins=["advanced_alchemy"],
        docker=False,
        docker_infra=True,
    )

    generator = LitestarGenerator(config, tmp_path)
    generator.generate()

    # Verify docker-compose.infra.yml exists
    docker_infra = tmp_path / "docker-compose.infra.yml"
    assert docker_infra.exists()
    content = docker_infra.read_text()

    # Check MySQL service
    assert "mysql:" in content
    assert "image: mysql:8.4.8-oraclelinux9" in content
    assert "3306:3306" in content
    assert "MYSQL_ROOT_PASSWORD" in content


def test_litestar_generator_valkey_context(tmp_path: Path) -> None:
    """Verify Litestar generator template context values with Valkey memory store."""
    config = ProjectConfig(
        name="Valkey Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.VALKEY,
        plugins=[],
        docker=False,
        docker_infra=True,
    )

    generator = LitestarGenerator(config, tmp_path)
    context = generator._get_template_context()

    assert context["has_store"] is True
    assert context["memory_store"] == MemoryStore.VALKEY
    assert context["store_config"].driver == "redis"
    assert context["store_config"].docker_image == "valkey/valkey:7.2.11-alpine3.23"


def test_litestar_generator_valkey_rendering(tmp_path: Path) -> None:
    """Verify that Valkey memory store is correctly rendered in docker-compose.infra.yml."""
    config = ProjectConfig(
        name="Valkey Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.VALKEY,
        plugins=[],
        docker=False,
        docker_infra=True,
    )

    generator = LitestarGenerator(config, tmp_path)
    generator.generate()

    # Verify docker-compose.infra.yml exists
    docker_infra = tmp_path / "docker-compose.infra.yml"
    assert docker_infra.exists()
    content = docker_infra.read_text()

    # Check Valkey service
    assert "valkey:" in content
    assert "image: valkey/valkey:7.2.11-alpine3.23" in content
    assert "6379:6379" in content


def test_litestar_generator_dockerfile_rendering(tmp_path: Path) -> None:
    """Verify that Dockerfile is correctly rendered with appropriate content."""
    config = ProjectConfig(
        name="Dockerfile Test",
        framework=Framework.LITESTAR,
        database=Database.POSTGRESQL,
        memory_store=MemoryStore.NONE,
        plugins=["advanced_alchemy"],
        docker=True,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)
    generator.generate()

    # Verify Dockerfile exists
    dockerfile = tmp_path / "Dockerfile"
    assert dockerfile.exists()
    content = dockerfile.read_text()

    # Check basic Dockerfile structure
    assert "FROM" in content
    assert "WORKDIR" in content
    assert "COPY" in content
    assert "RUN" in content
    assert "CMD" in content

    # Check for database migration command when advanced_alchemy is enabled
    has_migration_cmd = "litestar database upgrade" in content or "alembic upgrade head" in content
    assert has_migration_cmd, "No database migration command found in Dockerfile"


def test_litestar_generator_docker_infra_content(tmp_path: Path) -> None:
    """Verify docker-compose.infra.yml content is correctly rendered."""
    config = ProjectConfig(
        name="Infra Test",
        framework=Framework.LITESTAR,
        database=Database.POSTGRESQL,
        memory_store=MemoryStore.REDIS,
        plugins=[],
        docker=False,
        docker_infra=True,
    )

    generator = LitestarGenerator(config, tmp_path)
    generator.generate()

    # Verify docker-compose.infra.yml exists
    docker_infra = tmp_path / "docker-compose.infra.yml"
    assert docker_infra.exists()
    content = docker_infra.read_text()

    # Check PostgreSQL service
    assert "postgres:" in content
    assert "image: postgres:17.7-alpine3.23" in content
    assert "POSTGRES_USER" in content
    assert "POSTGRES_PASSWORD" in content
    assert "5432:5432" in content

    # Check Redis service
    assert "redis:" in content
    assert "image: redis:8.4.0-bookworm" in content
    assert "6379:6379" in content


def test_litestar_generator_multi_plugin_rendering(tmp_path: Path) -> None:
    """Verify that multiple plugins are correctly rendered together."""
    config = ProjectConfig(
        name="Multi Plugin Test",
        framework=Framework.LITESTAR,
        database=Database.POSTGRESQL,
        memory_store=MemoryStore.REDIS,
        plugins=["advanced_alchemy", "litestar_saq", "litestar_granian"],
        docker=False,
        docker_infra=True,
    )

    generator = LitestarGenerator(config, tmp_path)
    generator.generate()

    # Verify AdvancedAlchemy files
    assert (tmp_path / "src" / "backend" / "models" / "users.py").exists()
    assert (tmp_path / "src" / "backend" / "lib" / "dependencies.py").exists()

    # Verify SAQ files
    assert (tmp_path / "src" / "backend" / "lib" / "tasks.py").exists()

    # Verify app.py includes all plugins
    app_content = (tmp_path / "src" / "backend" / "app.py").read_text()
    assert "GranianPlugin" in app_content

    # Verify config.py includes all plugin configs
    config_content = (tmp_path / "src" / "backend" / "config.py").read_text()
    assert "alchemy" in config_content
    assert "saq" in config_content

    # Verify pyproject.toml includes all dependencies
    pyproject_content = (tmp_path / "pyproject.toml").read_text()
    assert "advanced-alchemy" in pyproject_content
    assert "litestar-saq" in pyproject_content
    assert "litestar-granian" in pyproject_content


def test_litestar_generator_vite_context(tmp_path: Path) -> None:
    """Verify Litestar generator template context values with Vite plugin enabled."""
    config = ProjectConfig(
        name="Vite Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=["litestar_vite"],
        docker=False,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)
    context = generator._get_template_context()

    assert context["litestar_vite"] is True


def test_litestar_generator_post_generate_no_plugins(tmp_path: Path) -> None:
    """Verify post_generate does nothing when no plugins are enabled."""
    config = ProjectConfig(
        name="Post Gen Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=[],
        docker=False,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)
    # Should not raise
    generator.post_generate()


def test_litestar_generator_post_generate_calls_plugin(tmp_path: Path, mocker: MockerFixture) -> None:
    """Verify post_generate calls post_generate on each enabled plugin."""
    config = ProjectConfig(
        name="Post Gen Test",
        framework=Framework.LITESTAR,
        database=Database.POSTGRESQL,
        memory_store=MemoryStore.NONE,
        plugins=["advanced_alchemy"],
        docker=False,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)

    # Mock all discovered plugins' post_generate
    for plugin in generator.plugins:
        mocker.patch.object(plugin, "post_generate")

    generator.post_generate()

    # Verify the enabled plugin's post_generate was called
    for plugin in generator.plugins:
        if config.has_plugin(plugin.id):
            plugin.post_generate.assert_called_once_with(config, tmp_path)
        else:
            plugin.post_generate.assert_not_called()
