from src.plugin import BasePlugin


class LitestarSAQPlugin(BasePlugin):
    """SAQ integration plugin for Litestar background tasks."""

    @property
    def name(self) -> str:  # noqa: D102
        return "Litestar SAQ (Background Tasks)"

    @property
    def description(self) -> str:  # noqa: D102
        return "SAQ integration for background tasks in Litestar"
