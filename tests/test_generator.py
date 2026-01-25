from pathlib import Path

from src.Litestar.generator import LitestarGenerator
from src.models import Database, Framework, ProjectConfig


def test_litestar_generator_context(tmp_path: Path) -> None:
    """Verify Litestar generator template context values with plugins and database enabled."""
    config = ProjectConfig(
        name="Test Project",
        framework=Framework.LITESTAR,
        database=Database.SQLITE,
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
        plugins=["advanced_alchemy"],
        docker=False,
        docker_infra=True,
    )

    generator = LitestarGenerator(config, tmp_path)
    generator.generate()

    # Verify base files
    assert (tmp_path / "pyproject.toml").exists()
    assert (tmp_path / "app.py").exists()

    # Verify AdvancedAlchemy plugin files
    # These are in src/Litestar/Plugins/AdvancedAlchemy/Templates/
    # Should be rendered to root of tmp_path (merging directories)
    assert (tmp_path / "models" / "users.py").exists()
    assert (tmp_path / "lib" / "dependencies.py").exists()
    assert (tmp_path / "lib" / "services.py").exists()
