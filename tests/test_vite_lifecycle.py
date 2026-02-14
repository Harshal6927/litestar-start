from pathlib import Path
from textwrap import dedent

import pytest

from src.Litestar.Plugins.LitestarVite import LitestarVitePlugin


@pytest.fixture
def app_file(tmp_path):
    """Create a temporary app.py file with bootstrap configuration."""
    content = dedent("""
    from litestar import Litestar
    from .config import settings
    from litestar_vite import ViteConfig, VitePlugin

    app = Litestar(
        plugins=[VitePlugin(config=ViteConfig(dev_mode=settings.DEBUG))],
    )
    """)
    file_path = tmp_path / "app.py"
    file_path.write_text(content.strip())
    return file_path


def test_update_app_config(app_file: Path) -> None:
    """Test that _update_app_config correctly updates app.py."""
    plugin = LitestarVitePlugin()

    # We expect this method to exist and perform the update
    # Since it's private, we access it directly for testing
    plugin._update_app_config(app_file)

    updated_content = app_file.read_text(encoding="utf-8")

    # Check imports
    assert "from .config import settings, vite_config" in updated_content
    assert "from litestar_vite import VitePlugin" in updated_content
    assert "from litestar_vite import ViteConfig, VitePlugin" not in updated_content

    # Check plugin config
    assert "VitePlugin(config=vite_config)" in updated_content
    assert "ViteConfig(dev_mode=settings.DEBUG)" not in updated_content


def test_update_app_config_idempotent(app_file: Path) -> None:
    """Test that running the update twice doesn't break anything."""
    plugin = LitestarVitePlugin()

    plugin._update_app_config(app_file)
    first_run_content = app_file.read_text(encoding="utf-8")

    plugin._update_app_config(app_file)
    second_run_content = app_file.read_text(encoding="utf-8")

    assert first_run_content == second_run_content
    assert "from .config import settings, vite_config" in second_run_content


def test_post_generate(tmp_path: Path, mocker) -> None:
    """Test post_generate calls subprocess and updates app config in correct location."""
    plugin = LitestarVitePlugin()

    # Mock subprocess.run
    mock_run = mocker.patch("subprocess.run")

    # Mock ProjectConfig
    config = mocker.Mock()

    # Setup src/backend/app.py
    backend_dir = tmp_path / "src" / "backend"
    backend_dir.mkdir(parents=True)
    app_file = backend_dir / "app.py"

    content = dedent("""
    from litestar import Litestar
    from .config import settings
    from litestar_vite import ViteConfig, VitePlugin

    app = Litestar(
        plugins=[VitePlugin(config=ViteConfig(dev_mode=settings.DEBUG))],
    )
    """)
    app_file.write_text(content.strip())

    plugin.post_generate(config, tmp_path)

    # Verify subprocess call
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == ["uv", "run", "litestar", "assets", "init", "--frontend-dir", "src/frontend"]
    assert kwargs["cwd"] == tmp_path

    # Verify app.py update
    updated_content = app_file.read_text(encoding="utf-8")
    assert "VitePlugin(config=vite_config)" in updated_content
