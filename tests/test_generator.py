from pathlib import Path

from src.Litestar.generator import LitestarGenerator
from src.models import Database, Framework, MemoryStore, ProjectConfig


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
    assert "from litestar_saq import QueueConfig, SAQConfig, SAQPlugin" in config_content
    assert "saq = SAQPlugin(" in config_content
    assert 'QueueConfig(name="default"' in config_content

    # Verify SAQ plugin in app.py
    app_content = (tmp_path / "src" / "backend" / "app.py").read_text()
    assert "from .config import saq" in app_content
    assert "saq," in app_content

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
    assert (tmp_path / "src" / "backend" / "__main__.py").exists()

    # Verify Granian plugin in app.py
    app_content = (tmp_path / "src" / "backend" / "app.py").read_text()
    assert "from litestar_granian import GranianPlugin" in app_content
    assert "GranianPlugin()," in app_content

    # Verify Granian in __main__.py (not uvicorn)
    main_content = (tmp_path / "src" / "backend" / "__main__.py").read_text()
    assert "from granian import Granian" in main_content
    assert "from granian.constants import Interfaces" in main_content
    assert "Granian(" in main_content
    assert "uvicorn" not in main_content

    # Verify Granian dependency in pyproject.toml
    pyproject_content = (tmp_path / "pyproject.toml").read_text()
    assert "litestar-granian>=0.14.2" in pyproject_content
