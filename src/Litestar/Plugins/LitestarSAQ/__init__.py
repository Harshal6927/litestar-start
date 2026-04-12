from src.models import MemoryStore, ProjectConfig
from src.plugin import BasePlugin


class LitestarSAQPlugin(BasePlugin):
    """SAQ integration plugin for Litestar background tasks."""

    @property
    def name(self) -> str:
        """Get the plugin display name.

        Returns:
            The display name shown in the CLI.

        """
        return "Litestar SAQ (Background Tasks)"

    @property
    def description(self) -> str:
        """Get the plugin description.

        Returns:
            A short description of the plugin.

        """
        return "SAQ integration for background tasks in Litestar"

    def is_applicable(self, config: ProjectConfig) -> bool:  # noqa: PLR6301
        """Check if this plugin is applicable for the given configuration.

        Args:
            config: The project configuration.

        Returns:
            True if a memory store (other than None) is selected.

        """
        return config.memory_store != MemoryStore.NONE
