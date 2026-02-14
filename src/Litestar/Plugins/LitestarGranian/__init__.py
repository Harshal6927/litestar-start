"""Litestar Granian plugin."""

from src.plugin import BasePlugin


class LitestarGranianPlugin(BasePlugin):
    """Granian ASGI server integration for Litestar."""

    @property
    def name(self) -> str:
        """Get the plugin name.

        Returns:
            The plugin name.

        """
        return "Litestar Granian (Server)"

    @property
    def description(self) -> str:
        """Get the plugin description.

        Returns:
            The plugin description.

        """
        return "Granian ASGI server integration for Litestar"
