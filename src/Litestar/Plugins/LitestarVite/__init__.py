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

    def post_generate(self, config: ProjectConfig, output_dir: Path) -> None:  # noqa: ARG002, PLR6301
        """Run Litestar Vite setup."""
        subprocess.run(
            ["uv", "run", "litestar", "assets", "init"],  # noqa: S607
            cwd=output_dir,
            check=True,
            capture_output=True,
        )
