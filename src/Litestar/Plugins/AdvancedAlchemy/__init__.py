from src.models import Database, ProjectConfig
from src.plugin import BasePlugin


class AdvancedAlchemyPlugin(BasePlugin):
    """Litestar plugin providing AdvancedAlchemy integration."""

    @property
    def name(self) -> str:  # noqa: D102
        return "AdvancedAlchemy (ORM)"

    @property
    def description(self) -> str:  # noqa: D102
        return "SQLAlchemy integration with Litestar"

    def is_applicable(self, config: ProjectConfig) -> bool:  # noqa: D102, PLR6301
        return config.database != Database.NONE
