# ruff: noqa: PLR6301
from pathlib import Path

from src.Litestar.Plugins.AdvancedAlchemy import AdvancedAlchemyPlugin
from src.Litestar.Plugins.LitestarSAQ import LitestarSAQPlugin
from src.models import Database, Framework, MemoryStore, ProjectConfig
from src.plugin import BasePlugin, Plugin, camel_to_snake, discover_plugins

MIN_PLUGIN_COUNT = 4


class TestCamelToSnake:
    """Tests for camel_to_snake function."""

    def test_single_word(self) -> None:
        """Verify camel_to_snake handles single word."""
        assert camel_to_snake("Plugin") == "plugin"
        assert camel_to_snake("Test") == "test"

    def test_two_words(self) -> None:
        """Verify camel_to_snake converts two-word CamelCase."""
        assert camel_to_snake("AdvancedAlchemy") == "advanced_alchemy"
        assert camel_to_snake("LitestarVite") == "litestar_vite"

    def test_three_words(self) -> None:
        """Verify camel_to_snake converts three-word CamelCase."""
        assert camel_to_snake("MyGreatPlugin") == "my_great_plugin"

    def test_consecutive_capitals(self) -> None:
        """Verify camel_to_snake handles consecutive capitals."""
        assert camel_to_snake("SAQPlugin") == "saq_plugin"
        assert camel_to_snake("HTTPServer") == "http_server"

    def test_already_lowercase(self) -> None:
        """Verify camel_to_snake handles already lowercase."""
        assert camel_to_snake("plugin") == "plugin"


class TestBasePlugin:
    """Tests for BasePlugin class."""

    def test_id_derived_from_class_name(self) -> None:
        """Verify BasePlugin.id is derived from class name."""

        class TestPlugin(BasePlugin):
            """Test plugin."""

            name = "Test"

        plugin = TestPlugin()
        assert plugin.id == "test"

    def test_id_removes_plugin_suffix(self) -> None:
        """Verify BasePlugin.id removes 'Plugin' suffix."""

        class MyCustomPlugin(BasePlugin):
            """Custom plugin."""

            name = "Custom"

        plugin = MyCustomPlugin()
        assert plugin.id == "my_custom"

    def test_description_default_empty(self) -> None:
        """Verify BasePlugin.description defaults to empty string."""

        class TestPlugin(BasePlugin):
            """Test plugin."""

            name = "Test"

        plugin = TestPlugin()
        assert not plugin.description

    def test_is_applicable_default_true(self) -> None:
        """Verify BasePlugin.is_applicable defaults to True."""

        class TestPlugin(BasePlugin):
            """Test plugin."""

            name = "Test"

        plugin = TestPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert plugin.is_applicable(config) is True

    def test_get_template_context_default_empty(self) -> None:
        """Verify BasePlugin.get_template_context defaults to empty dict."""

        class TestPlugin(BasePlugin):
            """Test plugin."""

            name = "Test"

        plugin = TestPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert plugin.get_template_context(config) == {}

    def test_post_generate_default_noop(self, tmp_path: Path) -> None:
        """Verify BasePlugin.post_generate defaults to no-op."""

        class TestPlugin(BasePlugin):
            """Test plugin."""

            name = "Test"

        plugin = TestPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        # Should not raise
        plugin.post_generate(config, tmp_path)


class TestDiscoverPlugins:
    """Tests for discover_plugins function."""

    def test_discover_litestar_plugins(self) -> None:
        """Verify Litestar plugins are discovered with expected metadata."""
        plugins = discover_plugins("Litestar")
        assert len(plugins) >= MIN_PLUGIN_COUNT

        ids = [p.id for p in plugins]
        assert "advanced_alchemy" in ids
        assert "litestar_saq" in ids
        assert "litestar_vite" in ids
        assert "litestar_granian" in ids

        for plugin in plugins:
            assert isinstance(plugin, Plugin)
            assert hasattr(plugin, "name")
            assert hasattr(plugin, "description")
            # Verify path attribute
            assert hasattr(plugin, "path"), f"Plugin {plugin.id} missing path attribute"
            assert isinstance(plugin.path, Path)
            assert plugin.path.exists()
            assert plugin.path.is_dir()

    def test_discover_nonexistent_framework(self) -> None:
        """Verify discover_plugins returns empty list for nonexistent framework."""
        plugins = discover_plugins("NonExistent")
        assert plugins == []


class TestAdvancedAlchemyPlugin:
    """Tests for AdvancedAlchemyPlugin."""

    def test_is_applicable_with_database(self) -> None:
        """Verify AdvancedAlchemyPlugin is applicable when database is configured."""
        plugin = AdvancedAlchemyPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.POSTGRESQL,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert plugin.is_applicable(config) is True

    def test_is_applicable_without_database(self) -> None:
        """Verify AdvancedAlchemyPlugin is not applicable when no database."""
        plugin = AdvancedAlchemyPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert plugin.is_applicable(config) is False


class TestLitestarSAQPlugin:
    """Tests for LitestarSAQPlugin."""

    def test_is_applicable_with_memory_store(self) -> None:
        """Verify LitestarSAQPlugin is applicable when memory store is configured."""
        plugin = LitestarSAQPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.REDIS,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert plugin.is_applicable(config) is True

    def test_is_applicable_without_memory_store(self) -> None:
        """Verify LitestarSAQPlugin is not applicable when no memory store."""
        plugin = LitestarSAQPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert plugin.is_applicable(config) is False
