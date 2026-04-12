from src.models import Database, ProjectConfig
from src.plugin import BasePlugin


class AdvancedAlchemyPlugin(BasePlugin):
    """Litestar plugin providing AdvancedAlchemy integration."""

    @property
    def name(self) -> str:
        """Get the plugin display name.

        Returns:
            The display name shown in the CLI.

        """
        return "AdvancedAlchemy (ORM)"

    @property
    def description(self) -> str:
        """Get the plugin description.

        Returns:
            A short description of the plugin.

        """
        return "SQLAlchemy integration with Litestar"

    def is_applicable(self, config: ProjectConfig) -> bool:  # noqa: PLR6301
        """Check if this plugin is applicable for the given configuration.

        Args:
            config: The project configuration.

        Returns:
            True if a database (other than None) is selected.

        """
        return config.database != Database.NONE
