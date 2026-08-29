# ruff: noqa: PLR6301
"""Unit tests for CLI functions."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from src.cli import (
    ask_database,
    ask_docker_dev_infra,
    ask_dockerfile,
    ask_framework,
    ask_memory_store,
    ask_plugins,
    ask_project_name,
    main,
    run_post_generation_setup,
)
from src.generator import ProjectGenerator
from src.Litestar.generator import LitestarGenerator
from src.models import Database, Framework, MemoryStore, ProjectConfig
from src.plugin import BasePlugin


class TestAskProjectName:
    """Tests for ask_project_name function."""

    def test_valid_name(self, mocker: MockerFixture) -> None:
        """Verify ask_project_name returns valid name."""
        mock_text = mocker.patch("questionary.text")
        mock_text.return_value.ask.return_value = "my-project"

        result = ask_project_name()
        assert result == "my-project"

    def test_validates_and_retries_on_invalid(self, mocker: MockerFixture) -> None:
        """Verify ask_project_name retries on invalid input."""
        mock_text = mocker.patch("questionary.text")
        mock_console = mocker.patch("src.cli.console")

        # First call returns invalid (empty), second call returns valid
        mock_text.return_value.ask.side_effect = ["", "valid-name"]

        result = ask_project_name()
        assert result == "valid-name"
        # Verify error message was printed
        mock_console.print.assert_called()

    def test_raises_system_exit_on_cancel(self, mocker: MockerFixture) -> None:
        """Verify ask_project_name raises SystemExit on Ctrl+C."""
        mock_text = mocker.patch("questionary.text")
        mock_text.return_value.ask.return_value = None  # User pressed Ctrl+C

        with pytest.raises(SystemExit) as exc_info:
            ask_project_name()

        assert exc_info.value.code == 0


class TestAskFramework:
    """Tests for ask_framework function."""

    def test_returns_selected_framework(self, mocker: MockerFixture) -> None:
        """Verify ask_framework returns selected framework."""
        mock_select = mocker.patch("questionary.select")
        mock_select.return_value.ask.return_value = Framework.LITESTAR

        result = ask_framework()
        assert result == Framework.LITESTAR

    def test_raises_system_exit_on_cancel(self, mocker: MockerFixture) -> None:
        """Verify ask_framework raises SystemExit on cancel."""
        mock_select = mocker.patch("questionary.select")
        mock_select.return_value.ask.return_value = None

        with pytest.raises(SystemExit) as exc_info:
            ask_framework()

        assert exc_info.value.code == 0


class TestAskDatabase:
    """Tests for ask_database function."""

    def test_returns_postgresql(self, mocker: MockerFixture) -> None:
        """Verify ask_database can return PostgreSQL."""
        mock_select = mocker.patch("questionary.select")
        mock_select.return_value.ask.return_value = Database.POSTGRESQL

        result = ask_database()
        assert result == Database.POSTGRESQL

    def test_returns_sqlite(self, mocker: MockerFixture) -> None:
        """Verify ask_database can return SQLite."""
        mock_select = mocker.patch("questionary.select")
        mock_select.return_value.ask.return_value = Database.SQLITE

        result = ask_database()
        assert result == Database.SQLITE

    def test_returns_mysql(self, mocker: MockerFixture) -> None:
        """Verify ask_database can return MySQL."""
        mock_select = mocker.patch("questionary.select")
        mock_select.return_value.ask.return_value = Database.MYSQL

        result = ask_database()
        assert result == Database.MYSQL

    def test_returns_none(self, mocker: MockerFixture) -> None:
        """Verify ask_database can return None."""
        mock_select = mocker.patch("questionary.select")
        mock_select.return_value.ask.return_value = Database.NONE

        result = ask_database()
        assert result == Database.NONE

    def test_raises_system_exit_on_cancel(self, mocker: MockerFixture) -> None:
        """Verify ask_database raises SystemExit on cancel."""
        mock_select = mocker.patch("questionary.select")
        mock_select.return_value.ask.return_value = None

        with pytest.raises(SystemExit) as exc_info:
            ask_database()

        assert exc_info.value.code == 0


class TestAskMemoryStore:
    """Tests for ask_memory_store function."""

    def test_returns_redis(self, mocker: MockerFixture) -> None:
        """Verify ask_memory_store can return Redis."""
        mock_select = mocker.patch("questionary.select")
        mock_select.return_value.ask.return_value = MemoryStore.REDIS

        result = ask_memory_store()
        assert result == MemoryStore.REDIS

    def test_returns_valkey(self, mocker: MockerFixture) -> None:
        """Verify ask_memory_store can return Valkey."""
        mock_select = mocker.patch("questionary.select")
        mock_select.return_value.ask.return_value = MemoryStore.VALKEY

        result = ask_memory_store()
        assert result == MemoryStore.VALKEY

    def test_returns_none(self, mocker: MockerFixture) -> None:
        """Verify ask_memory_store can return None."""
        mock_select = mocker.patch("questionary.select")
        mock_select.return_value.ask.return_value = MemoryStore.NONE

        result = ask_memory_store()
        assert result == MemoryStore.NONE

    def test_raises_system_exit_on_cancel(self, mocker: MockerFixture) -> None:
        """Verify ask_memory_store raises SystemExit on cancel."""
        mock_select = mocker.patch("questionary.select")
        mock_select.return_value.ask.return_value = None

        with pytest.raises(SystemExit) as exc_info:
            ask_memory_store()

        assert exc_info.value.code == 0


class TestAskPlugins:
    """Tests for ask_plugins function."""

    def test_returns_selected_plugins(self, mocker: MockerFixture) -> None:
        """Verify ask_plugins returns selected plugin IDs."""
        mock_checkbox = mocker.patch("questionary.checkbox")
        mock_checkbox.return_value.ask.return_value = ["plugin1", "plugin2"]

        class MockPlugin1(BasePlugin):
            name = "Plugin 1"

            @property
            def id(self) -> str:
                return "plugin1"

        class MockPlugin2(BasePlugin):
            name = "Plugin 2"

            @property
            def id(self) -> str:
                return "plugin2"

        plugin1 = MockPlugin1()
        plugin2 = MockPlugin2()

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )

        result = ask_plugins(config, [plugin1, plugin2])
        assert result == ["plugin1", "plugin2"]

    def test_filters_non_applicable_plugins(self, mocker: MockerFixture) -> None:
        """Verify ask_plugins filters out non-applicable plugins."""
        mock_checkbox = mocker.patch("questionary.checkbox")
        mock_checkbox.return_value.ask.return_value = ["applicable_plugin"]

        class ApplicablePlugin(BasePlugin):
            name = "Applicable"

            @property
            def id(self) -> str:
                return "applicable_plugin"

            def is_applicable(self, config: ProjectConfig) -> bool:  # noqa: ARG002
                return True

        class NotApplicablePlugin(BasePlugin):
            name = "Not Applicable"

            @property
            def id(self) -> str:
                return "not_applicable"

            def is_applicable(self, config: ProjectConfig) -> bool:  # noqa: ARG002
                return False

        plugin1 = ApplicablePlugin()
        plugin2 = NotApplicablePlugin()

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )

        ask_plugins(config, [plugin1, plugin2])

        # Verify checkbox was called with only applicable plugin
        call_kwargs = mock_checkbox.call_args[1]
        choices = call_kwargs["choices"]
        assert len(choices) == 1
        assert choices[0].value == "applicable_plugin"

    def test_returns_empty_list_when_no_applicable_plugins(self, mocker: MockerFixture) -> None:  # noqa: ARG002
        """Verify ask_plugins returns empty list when no plugins are applicable."""

        class NotApplicablePlugin(BasePlugin):
            name = "Not Applicable"

            @property
            def id(self) -> str:
                return "not_applicable"

            def is_applicable(self, config: ProjectConfig) -> bool:  # noqa: ARG002
                return False

        plugin = NotApplicablePlugin()

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )

        result = ask_plugins(config, [plugin])
        assert result == []

    def test_raises_system_exit_on_cancel(self, mocker: MockerFixture) -> None:
        """Verify ask_plugins raises SystemExit on cancel."""
        mock_checkbox = mocker.patch("questionary.checkbox")
        mock_checkbox.return_value.ask.return_value = None

        class MockPlugin(BasePlugin):
            name = "Mock"

            @property
            def id(self) -> str:
                return "mock"

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=False,
        )

        with pytest.raises(SystemExit) as exc_info:
            ask_plugins(config, [MockPlugin()])

        assert exc_info.value.code == 0


class TestAskDockerfile:
    """Tests for ask_dockerfile function."""

    def test_returns_true(self, mocker: MockerFixture) -> None:
        """Verify ask_dockerfile returns True when selected."""
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = True

        result = ask_dockerfile()
        assert result is True

    def test_returns_false(self, mocker: MockerFixture) -> None:
        """Verify ask_dockerfile returns False when not selected."""
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

        result = ask_dockerfile()
        assert result is False

    def test_raises_system_exit_on_cancel(self, mocker: MockerFixture) -> None:
        """Verify ask_dockerfile raises SystemExit on cancel."""
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = None

        with pytest.raises(SystemExit) as exc_info:
            ask_dockerfile()

        assert exc_info.value.code == 0


class TestAskDockerDevInfra:
    """Tests for ask_docker_dev_infra function."""

    def test_returns_true(self, mocker: MockerFixture) -> None:
        """Verify ask_docker_dev_infra returns True when selected."""
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = True

        result = ask_docker_dev_infra()
        assert result is True

    def test_returns_false(self, mocker: MockerFixture) -> None:
        """Verify ask_docker_dev_infra returns False when not selected."""
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

        result = ask_docker_dev_infra()
        assert result is False

    def test_raises_system_exit_on_cancel(self, mocker: MockerFixture) -> None:
        """Verify ask_docker_dev_infra raises SystemExit on cancel."""
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = None

        with pytest.raises(SystemExit) as exc_info:
            ask_docker_dev_infra()

        assert exc_info.value.code == 0


class TestRunPostGenerationSetup:
    """Tests for run_post_generation_setup function."""

    def test_runs_git_init(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify run_post_generation_setup runs git init."""
        mock_run = mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False  # Don't start app

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
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        # Find the git init call
        git_calls = [call for call in mock_run.call_args_list if call[0][0][0] == "git"]
        assert len(git_calls) >= 1
        assert git_calls[0][0][0] == ["git", "init"]

    def test_runs_uv_sync(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify run_post_generation_setup runs uv sync."""
        mock_run = mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

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
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        # Find the uv sync call
        uv_calls = [call for call in mock_run.call_args_list if call[0][0][0] == "uv"]
        assert any(call[0][0] == ["uv", "sync"] for call in uv_calls)

    def test_runs_docker_compose_when_docker_dev_infra(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Verify run_post_generation_setup runs compose when docker_dev_infra is True and docker is available."""
        mocker.patch("src.cli.get_container_engine", return_value="docker")
        mock_run = mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.POSTGRESQL,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=True,
        )
        generator = ProjectGenerator(config, tmp_path)
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        # Find the docker compose call
        docker_calls = [call for call in mock_run.call_args_list if call[0][0][0] == "docker"]
        assert len(docker_calls) >= 1
        assert "docker-compose.dev-infra.yml" in docker_calls[0][0][0]

    def test_runs_podman_compose_when_docker_missing_and_podman_available(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Verify run_post_generation_setup runs podman compose when podman is available."""
        mocker.patch("src.cli.get_container_engine", return_value="podman")
        mock_run = mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.POSTGRESQL,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=True,
        )
        generator = ProjectGenerator(config, tmp_path)
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        # Find the podman compose call
        podman_calls = [call for call in mock_run.call_args_list if call[0][0][0] == "podman"]
        assert len(podman_calls) >= 1
        assert podman_calls[0][0][0] == ["podman", "compose", "-f", "docker-compose.dev-infra.yml", "up", "-d"]

    def test_prompts_and_uses_custom_engine_when_neither_available(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Verify run_post_generation_setup prompts and uses custom engine when docker/podman are missing."""
        mocker.patch("src.cli.get_container_engine", return_value=None)
        mock_run = mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        # First confirm is for custom engine (True), second confirm is for start app (False)
        mock_confirm.return_value.ask.side_effect = [True, False]
        mock_text = mocker.patch("questionary.text")
        mock_text.return_value.ask.return_value = "nerdctl"

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.POSTGRESQL,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=True,
        )
        generator = ProjectGenerator(config, tmp_path)
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        # Find the custom engine compose call
        custom_calls = [call for call in mock_run.call_args_list if call[0][0][0] == "nerdctl"]
        assert len(custom_calls) >= 1
        assert custom_calls[0][0][0] == ["nerdctl", "compose", "-f", "docker-compose.dev-infra.yml", "up", "-d"]

    def test_skips_infra_when_neither_available_and_user_declines(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Verify run_post_generation_setup skips infra startup when user declines custom engine."""
        mocker.patch("src.cli.get_container_engine", return_value=None)
        mock_run = mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        # First confirm is for custom engine (False), second confirm is for start app (False)
        mock_confirm.return_value.ask.side_effect = [False, False]

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.POSTGRESQL,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=True,
        )
        generator = ProjectGenerator(config, tmp_path)
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        # Verify no compose calls made
        compose_calls = [call for call in mock_run.call_args_list if len(call[0][0]) > 1 and call[0][0][1] == "compose"]
        assert len(compose_calls) == 0

    def test_skips_infra_when_user_cancels_custom_engine_prompt(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Verify run_post_generation_setup skips infra startup when user cancels custom engine input."""
        mocker.patch("src.cli.get_container_engine", return_value=None)
        mock_run = mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        # First confirm is for custom engine (True), second confirm is for start app (False)
        mock_confirm.return_value.ask.side_effect = [True, False]
        mock_text = mocker.patch("questionary.text")
        mock_text.return_value.ask.return_value = None

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.POSTGRESQL,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=True,
        )
        generator = ProjectGenerator(config, tmp_path)
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        # Verify no compose calls made
        compose_calls = [call for call in mock_run.call_args_list if len(call[0][0]) > 1 and call[0][0][1] == "compose"]
        assert len(compose_calls) == 0

    def test_skips_docker_compose_when_not_needed(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify run_post_generation_setup skips docker compose when not needed."""
        mock_run = mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.SQLITE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_dev_infra=True,
        )
        generator = ProjectGenerator(config, tmp_path)
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        # Verify no docker compose calls
        docker_calls = [call for call in mock_run.call_args_list if call[0][0][0] == "docker"]
        assert len(docker_calls) == 0

    def test_copies_gitignore_to_dockerignore_when_docker(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify run_post_generation_setup copies .gitignore to .dockerignore when docker is True."""
        mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

        # Create .gitignore
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n")

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=True,
            docker_dev_infra=False,
        )
        generator = ProjectGenerator(config, tmp_path)
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        # Verify .dockerignore was created
        dockerignore = tmp_path / ".dockerignore"
        assert dockerignore.exists()
        assert dockerignore.read_text() == "*.pyc\n"

    def test_calls_post_generate(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify run_post_generation_setup calls generator.post_generate."""
        mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

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
        mock_post_generate = mocker.Mock()
        generator.post_generate = mock_post_generate

        run_post_generation_setup(generator, tmp_path)

        mock_post_generate.assert_called_once()

    def test_runs_ruff_import_sorting(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify run_post_generation_setup runs ruff for import sorting."""
        mock_run = mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

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
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        # Find the ruff call
        ruff_calls = [call for call in mock_run.call_args_list if "ruff" in call[0][0]]
        assert len(ruff_calls) >= 1
        assert "check" in ruff_calls[0][0][0]
        assert "--select" in ruff_calls[0][0][0]
        assert "I" in ruff_calls[0][0][0]

    def test_copies_env_example_to_env(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify run_post_generation_setup copies .env.example to .env."""
        mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

        # Create .env.example
        env_example = tmp_path / ".env.example"
        env_example.write_text("DATABASE_URL=sqlite:///app.db\n")

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
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        env_file = tmp_path / ".env"
        assert env_file.exists()
        assert env_file.read_text() == "DATABASE_URL=sqlite:///app.db\n"

    def test_skips_env_copy_when_no_example(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify run_post_generation_setup skips .env copy when .env.example doesn't exist."""
        mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

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
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        env_file = tmp_path / ".env"
        assert not env_file.exists()

    def test_skips_dockerignore_when_no_docker(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify .dockerignore is NOT created when docker is False."""
        mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

        # Create .gitignore but docker=False
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n")

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
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        dockerignore = tmp_path / ".dockerignore"
        assert not dockerignore.exists()

    def test_skips_dockerignore_when_no_gitignore(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify .dockerignore is NOT created when .gitignore doesn't exist."""
        mocker.patch("subprocess.run")
        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=True,
            docker_dev_infra=False,
        )
        generator = ProjectGenerator(config, tmp_path)
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        run_post_generation_setup(generator, tmp_path)

        dockerignore = tmp_path / ".dockerignore"
        assert not dockerignore.exists()


class TestSubprocessFailures:
    """Tests for subprocess failure paths in run_post_generation_setup."""

    def test_git_init_failure_raises(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify CalledProcessError from git init propagates."""
        import subprocess as sp

        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = sp.CalledProcessError(128, ["git", "init"])

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
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        with pytest.raises(sp.CalledProcessError):
            run_post_generation_setup(generator, tmp_path)

    def test_uv_sync_failure_raises(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify CalledProcessError from uv sync propagates."""
        import subprocess as sp

        call_count = 0
        uv_sync_call_number = 2

        def selective_fail(*args: object, **kwargs: object) -> None:  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            if call_count == uv_sync_call_number:  # uv sync is the second subprocess call
                raise sp.CalledProcessError(1, ["uv", "sync"])

        mocker.patch("subprocess.run", side_effect=selective_fail)

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
        generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

        with pytest.raises(sp.CalledProcessError):
            run_post_generation_setup(generator, tmp_path)


class TestMain:
    """Tests for main() CLI entry point."""

    def test_main_happy_path(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Verify main() orchestrates the full project generation flow."""
        mocker.patch("src.cli.print_banner")
        mocker.patch("src.cli.ask_project_name", return_value="test-project")
        mocker.patch("src.cli.ask_framework", return_value=Framework.LITESTAR)
        mocker.patch("src.cli.ask_database", return_value=Database.NONE)
        mocker.patch("src.cli.ask_memory_store", return_value=MemoryStore.NONE)
        mocker.patch("src.cli.discover_plugins", return_value=[])
        mocker.patch("src.cli.ask_plugins", return_value=[])
        mocker.patch("src.cli.ask_dockerfile", return_value=False)
        mock_dev_infra = mocker.patch("src.cli.ask_docker_dev_infra")

        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = True  # Confirm generation

        mock_generator_cls = mocker.patch("src.cli.ProjectGenerator")
        mock_generator = mock_generator_cls.return_value

        # Mock Path.cwd() to use tmp_path
        mocker.patch("src.cli.Path.cwd", return_value=tmp_path)

        mock_post_gen = mocker.patch("src.cli.run_post_generation_setup")

        main()

        mock_dev_infra.assert_not_called()
        mock_generator_cls.assert_called_once()
        mock_generator.generate.assert_called_once()
        mock_post_gen.assert_called_once()

    def test_main_user_cancels_confirmation(self, mocker: MockerFixture) -> None:
        """Verify main() exits when user declines confirmation."""
        mocker.patch("src.cli.print_banner")
        mocker.patch("src.cli.ask_project_name", return_value="test-project")
        mocker.patch("src.cli.ask_framework", return_value=Framework.LITESTAR)
        mocker.patch("src.cli.ask_database", return_value=Database.NONE)
        mocker.patch("src.cli.ask_memory_store", return_value=MemoryStore.NONE)
        mocker.patch("src.cli.discover_plugins", return_value=[])
        mocker.patch("src.cli.ask_plugins", return_value=[])
        mocker.patch("src.cli.ask_dockerfile", return_value=False)

        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False  # Decline

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    def test_main_skips_docker_dev_infra_for_sqlite_without_memory_store(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Verify main() does not prompt for docker dev infra when SQLite and no memory store are selected."""
        mocker.patch("src.cli.print_banner")
        mocker.patch("src.cli.ask_project_name", return_value="test-project")
        mocker.patch("src.cli.ask_framework", return_value=Framework.LITESTAR)
        mocker.patch("src.cli.ask_database", return_value=Database.SQLITE)
        mocker.patch("src.cli.ask_memory_store", return_value=MemoryStore.NONE)
        mocker.patch("src.cli.discover_plugins", return_value=[])
        mocker.patch("src.cli.ask_plugins", return_value=[])
        mocker.patch("src.cli.ask_dockerfile", return_value=True)
        mock_dev_infra = mocker.patch("src.cli.ask_docker_dev_infra")

        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = True

        mock_generator_cls = mocker.patch("src.cli.ProjectGenerator")
        mocker.patch("src.cli.Path.cwd", return_value=tmp_path)
        mocker.patch("src.cli.run_post_generation_setup")

        main()

        mock_dev_infra.assert_not_called()
        config: ProjectConfig = mock_generator_cls.call_args[0][0]
        assert config.docker is True
        assert config.docker_dev_infra is False

    def test_main_prompts_docker_dev_infra_when_database_supports_it(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Verify main() prompts for docker dev infra when PostgreSQL is selected."""
        mocker.patch("src.cli.print_banner")
        mocker.patch("src.cli.ask_project_name", return_value="test-project")
        mocker.patch("src.cli.ask_framework", return_value=Framework.LITESTAR)
        mocker.patch("src.cli.ask_database", return_value=Database.POSTGRESQL)
        mocker.patch("src.cli.ask_memory_store", return_value=MemoryStore.NONE)
        mocker.patch("src.cli.discover_plugins", return_value=[])
        mocker.patch("src.cli.ask_plugins", return_value=[])
        mocker.patch("src.cli.ask_dockerfile", return_value=True)
        mock_dev_infra = mocker.patch("src.cli.ask_docker_dev_infra", return_value=True)

        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = True

        mock_generator_cls = mocker.patch("src.cli.ProjectGenerator")
        mocker.patch("src.cli.Path.cwd", return_value=tmp_path)
        mocker.patch("src.cli.run_post_generation_setup")

        main()

        mock_dev_infra.assert_called_once()
        config: ProjectConfig = mock_generator_cls.call_args[0][0]
        assert config.docker is True
        assert config.docker_dev_infra is True

    def test_main_prompts_docker_dev_infra_when_memory_store_supports_it(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Verify main() prompts for docker dev infra when Valkey is selected with SQLite."""
        mocker.patch("src.cli.print_banner")
        mocker.patch("src.cli.ask_project_name", return_value="test-project")
        mocker.patch("src.cli.ask_framework", return_value=Framework.LITESTAR)
        mocker.patch("src.cli.ask_database", return_value=Database.SQLITE)
        mocker.patch("src.cli.ask_memory_store", return_value=MemoryStore.VALKEY)
        mocker.patch("src.cli.discover_plugins", return_value=[])
        mocker.patch("src.cli.ask_plugins", return_value=[])
        mocker.patch("src.cli.ask_dockerfile", return_value=False)
        mock_dev_infra = mocker.patch("src.cli.ask_docker_dev_infra", return_value=False)

        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = True

        mock_generator_cls = mocker.patch("src.cli.ProjectGenerator")
        mocker.patch("src.cli.Path.cwd", return_value=tmp_path)
        mocker.patch("src.cli.run_post_generation_setup")

        main()

        mock_dev_infra.assert_called_once()
        config: ProjectConfig = mock_generator_cls.call_args[0][0]
        assert config.docker is False
        assert config.docker_dev_infra is False

    def test_main_keyboard_interrupt(self, mocker: MockerFixture) -> None:
        """Verify main() handles KeyboardInterrupt gracefully."""
        mocker.patch("src.cli.print_banner")
        mocker.patch("src.cli.ask_project_name", side_effect=KeyboardInterrupt)

        # Should not raise — main() catches KeyboardInterrupt
        main()
