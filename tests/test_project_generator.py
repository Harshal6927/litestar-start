# ruff: noqa: PLR6301
"""Unit tests for the ProjectGenerator orchestrator."""

from pathlib import Path
from typing import cast

import pytest
from pytest_mock import MockerFixture

from src.generator import ProjectGenerator
from src.models import Database, Framework, MemoryStore, ProjectConfig


class TestProjectGenerator:
    """Tests for ProjectGenerator orchestrator."""

    def test_generate_litestar_framework(self, tmp_path: Path) -> None:
        """Verify generate dispatches to LitestarGenerator for Litestar framework."""
        config = ProjectConfig(
            name="Test Project",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )

        generator = ProjectGenerator(config, tmp_path)
        generator.generate()

        # Verify basic project structure was created
        assert tmp_path.exists()
        assert (tmp_path / "pyproject.toml").exists()
        assert (tmp_path / "src" / "backend").exists()

    def test_generate_creates_output_directory(self, tmp_path: Path) -> None:
        """Verify generate creates the output directory."""
        output_dir = tmp_path / "new_project"
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )

        generator = ProjectGenerator(config, output_dir)
        generator.generate()

        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_post_generate_delegates_to_framework_generator(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify post_generate delegates to framework generator."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )

        generator = ProjectGenerator(config, tmp_path)
        generator.generate()

        # Mock the framework generator's post_generate method
        mock_post_generate = mocker.patch.object(generator._framework_generator, "post_generate")

        generator.post_generate()

        # Verify it was called
        mock_post_generate.assert_called_once()

    def test_post_generate_when_no_framework_generator(self, tmp_path: Path) -> None:
        """Verify post_generate is safe when no framework generator exists."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )

        generator = ProjectGenerator(config, tmp_path)
        # Don't call generate(), so _framework_generator is None

        # Should not raise
        generator.post_generate()

    def test_generate_unsupported_framework_raises(self, tmp_path: Path) -> None:
        """Verify generate raises NotImplementedError for unsupported framework."""
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )

        generator = ProjectGenerator(config, tmp_path)
        # Monkeypatch the framework to a value that's not handled

        generator.config = ProjectConfig(
            name="Test",
            framework=cast("Framework", "UnsupportedFramework"),
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )

        with pytest.raises(NotImplementedError, match="not yet supported"):
            generator.generate()
