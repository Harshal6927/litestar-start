import subprocess  # noqa: S404
from pathlib import Path

from src.models import ProjectConfig
from src.plugin import BasePlugin


class LitestarVitePlugin(BasePlugin):
    """Plugin providing Vite integration for Litestar frontend assets."""

    @property
    def name(self) -> str:  # noqa: D102
        return "Litestar Vite (Frontend Integration)"

    @property
    def description(self) -> str:  # noqa: D102
        return "Vite integration for frontend assets in Litestar"

    def post_generate(self, config: ProjectConfig, output_dir: Path) -> None:  # noqa: ARG002
        """Run Litestar Vite setup."""
        subprocess.run(
            ["uv", "run", "litestar", "assets", "init", "--frontend-dir", "src/frontend"],  # noqa: S607
            cwd=output_dir,
            check=True,
        )
        self._update_app_config(output_dir / "src" / "backend" / "app.py")

    def _update_app_config(self, app_path: Path) -> None:
        """Update app.py to use the full Vite config from config.py."""
        if not app_path.exists():
            return

        content = app_path.read_text(encoding="utf-8")

        # Update imports
        if "from config import settings" in content and "vite_config" not in content:
            content = content.replace("from config import settings", "from config import settings, vite_config")

        if "from litestar_vite import ViteConfig, VitePlugin" in content:
            content = content.replace(
                "from litestar_vite import ViteConfig, VitePlugin",
                "from litestar_vite import VitePlugin",
            )

        # Update plugin config
        bootstrap_config = "VitePlugin(config=ViteConfig(dev_mode=settings.DEBUG))"
        full_config = "VitePlugin(config=vite_config)"

        if bootstrap_config in content:
            content = content.replace(bootstrap_config, full_config)

        app_path.write_text(content, encoding="utf-8")
