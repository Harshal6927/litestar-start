# ruff: noqa: PLR6301
"""Unit tests for LitestarGranianPlugin."""

from src.Litestar.Plugins.LitestarGranian import LitestarGranianPlugin
from src.models import Database, Framework, MemoryStore, ProjectConfig


class TestLitestarGranianPlugin:
    """Tests for LitestarGranianPlugin."""

    def test_plugin_id(self) -> None:
        """Verify plugin ID is derived correctly from class name."""
        plugin = LitestarGranianPlugin()
        assert plugin.id == "litestar_granian"

    def test_plugin_name(self) -> None:
        """Verify plugin display name."""
        plugin = LitestarGranianPlugin()
        assert plugin.name == "Litestar Granian (Server)"

    def test_plugin_description(self) -> None:
        """Verify plugin description is set."""
        plugin = LitestarGranianPlugin()
        assert "Granian" in plugin.description

    def test_is_applicable_always_true(self) -> None:
        """Verify Granian plugin is always applicable (inherits BasePlugin default)."""
        plugin = LitestarGranianPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )
        assert plugin.is_applicable(config) is True

    def test_is_applicable_with_database(self) -> None:
        """Verify Granian plugin is applicable even with database configured."""
        plugin = LitestarGranianPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.POSTGRESQL,
            memory_store=MemoryStore.REDIS,
            plugins=["litestar_granian"],
            docker=True,
            docker_dev_infra=True,
        )
        assert plugin.is_applicable(config) is True

    def test_get_template_context_empty(self) -> None:
        """Verify Granian plugin returns empty template context (inherits default)."""
        plugin = LitestarGranianPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )
        assert plugin.get_template_context(config) == {}
