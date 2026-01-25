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
