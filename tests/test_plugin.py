from pathlib import Path

from src.plugin import Plugin, discover_plugins

MIN_PLUGIN_COUNT = 3


def test_discover_litestar_plugins() -> None:
    """Verify Litestar plugins are discovered with expected metadata."""
    plugins = discover_plugins("Litestar")
    assert len(plugins) >= MIN_PLUGIN_COUNT

    ids = [p.id for p in plugins]
    assert "advanced_alchemy" in ids
    assert "litestar_saq" in ids
    assert "litestar_vite" in ids

    for plugin in plugins:
        assert isinstance(plugin, Plugin)
        assert hasattr(plugin, "name")
        assert hasattr(plugin, "description")
        # Verify path attribute
        assert hasattr(plugin, "path"), f"Plugin {plugin.id} missing path attribute"
        assert isinstance(plugin.path, Path)
        assert plugin.path.exists()
        assert plugin.path.is_dir()
