"""Shared test fixtures."""

from collections.abc import Callable
from pathlib import Path

import pytest

from src.models import Database, Framework, MemoryStore, ProjectConfig


@pytest.fixture
def make_config() -> Callable[..., ProjectConfig]:
    """Factory fixture to create ProjectConfig with sensible defaults.

    Returns:
        A callable that creates ProjectConfig instances with overridable defaults.

    """

    def _make_config(  # noqa: PLR0913, PLR0917
        name: str = "Test",
        framework: Framework = Framework.LITESTAR,
        database: Database = Database.NONE,
        memory_store: MemoryStore = MemoryStore.NONE,
        plugins: list[str] | None = None,
        docker: bool = False,  # noqa: FBT001, FBT002
        docker_infra: bool = False,  # noqa: FBT001, FBT002
    ) -> ProjectConfig:
        return ProjectConfig(
            name=name,
            framework=framework,
            database=database,
            memory_store=memory_store,
            plugins=plugins or [],
            docker=docker,
            docker_infra=docker_infra,
        )

    return _make_config


@pytest.fixture
def sample_config(make_config: Callable[..., ProjectConfig]) -> ProjectConfig:
    """A minimal default ProjectConfig for simple tests.

    Returns:
        A ProjectConfig with all defaults (no database, no plugins, no docker).

    """
    return make_config()


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Provide a clean temporary output directory for generators.

    Returns:
        A Path to a temporary directory.

    """
    return tmp_path
