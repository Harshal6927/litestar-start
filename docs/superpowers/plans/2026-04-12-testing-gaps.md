# Testing Gaps Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close all testing gaps identified in audit items #25-38: add shared fixtures, missing test coverage, fix weak assertions, improve mock quality, and add boundary tests.

**Architecture:** Start with foundational infrastructure (conftest.py with fixtures), then add missing test coverage for untested code paths, fix existing weak tests, and finish with structural improvements. Each task is independently committable.

**Tech Stack:** Python 3.13+, pytest, pytest-mock, msgspec

---

## File Map

- Create: `tests/conftest.py` — shared fixtures (`make_config` factory, common mocks)
- Modify: `tests/test_utils.py` — add boundary tests for `slugify()` and `validate_project_name()`
- Modify: `tests/test_generator.py` — fix OR-assertions (lines 183, 361), will be renamed to `tests/test_litestar_generator.py`
- Modify: `tests/test_cli.py` — add `spec=` to mocks, add `main()` tests, add subprocess failure tests, add `.env`/`.dockerignore` copy tests
- Modify: `tests/test_plugin.py` — add `discover_plugins` error branch test
- Modify: `tests/test_project_generator.py` — add `NotImplementedError` test
- Create: `tests/test_granian_plugin.py` — direct tests for `LitestarGranianPlugin`

---

### Task 1: Create `tests/conftest.py` with shared fixtures (#25)

`ProjectConfig` is constructed 40+ times across test files with identical boilerplate. A factory fixture reduces this.

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: Create `tests/conftest.py` with `make_config` factory fixture**

```python
"""Shared test fixtures."""

from pathlib import Path

import pytest

from src.models import Database, Framework, MemoryStore, ProjectConfig


@pytest.fixture
def make_config():
    """Factory fixture to create ProjectConfig with sensible defaults.

    Returns:
        A callable that creates ProjectConfig instances with overridable defaults.

    """

    def _make_config(
        name: str = "Test",
        framework: Framework = Framework.LITESTAR,
        database: Database = Database.NONE,
        memory_store: MemoryStore = MemoryStore.NONE,
        plugins: list[str] | None = None,
        docker: bool = False,
        docker_infra: bool = False,
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
def sample_config(make_config):
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
```

- [ ] **Step 2: Verify fixtures are discovered**

Run: `pytest --collect-only tests/conftest.py`
Expected: No errors. Fixtures should be discovered by pytest automatically.

- [ ] **Step 3: Run full test suite to verify no regressions**

Run: `pytest -v`
Expected: All existing tests PASS. The new fixtures don't interfere with anything.

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py
git commit -m "test: add conftest.py with shared ProjectConfig factory fixture"
```

---

### Task 2: Add boundary tests for `slugify()` and `validate_project_name()` (#37)

Missing boundary tests: unicode input, consecutive hyphens, max length boundary (49 vs 50 vs 51 chars).

**Files:**
- Modify: `tests/test_utils.py` — add test methods to `TestSlugify` and `TestValidateProjectName`

- [ ] **Step 1: Add boundary tests to `TestSlugify` class in `tests/test_utils.py`**

Add these methods to the existing `TestSlugify` class (after the `test_mixed_case_spaces_hyphens` method):

```python
def test_unicode_characters(self) -> None:
    """Verify slugify strips unicode characters."""
    assert slugify("café") == "caf"
    assert slugify("naïve") == "nave"

def test_consecutive_hyphens(self) -> None:
    """Verify slugify collapses consecutive hyphens to single underscore."""
    assert slugify("my--project") == "my_project"
    assert slugify("a---b") == "a_b"

def test_consecutive_spaces(self) -> None:
    """Verify slugify collapses consecutive spaces to single underscore."""
    assert slugify("my   project") == "my_project"

def test_mixed_consecutive_separators(self) -> None:
    """Verify slugify collapses mixed hyphens/spaces to single underscore."""
    assert slugify("my - project") == "my_project"
    assert slugify("a - - b") == "a_b"

def test_leading_trailing_separators(self) -> None:
    """Verify slugify handles leading/trailing hyphens and spaces."""
    assert slugify("-project-") == "_project_"
    assert slugify(" project ") == "_project_"

def test_underscores_preserved(self) -> None:
    """Verify slugify preserves existing underscores."""
    assert slugify("my_project") == "my_project"
```

- [ ] **Step 2: Add boundary tests to `TestValidateProjectName` class in `tests/test_utils.py`**

Add these methods to the existing `TestValidateProjectName` class:

```python
def test_max_length_boundary(self) -> None:
    """Verify validate_project_name at exact 50-char boundary."""
    assert validate_project_name("x" * 49) is None
    assert validate_project_name("x" * 50) is None
    error = validate_project_name("x" * 51)
    assert error is not None
    assert "50" in error

def test_numeric_only_name(self) -> None:
    """Verify validate_project_name accepts numeric-only names (slugified to _123)."""
    assert validate_project_name("123") is None
```

- [ ] **Step 3: Run new tests**

Run: `pytest tests/test_utils.py -k "boundary or unicode or consecutive or leading or underscores_preserved or numeric_only" -v`
Expected: All PASS.

- [ ] **Step 4: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_utils.py
git commit -m "test: add boundary tests for slugify and validate_project_name"
```

---

### Task 3: Fix OR-assertions in `test_generator.py` (#31)

Two assertions use `assert X or Y` which always passes if the first condition is truthy. These should use separate assertions or `any()`.

**Files:**
- Modify: `tests/test_generator.py:183,361`

- [ ] **Step 1: Fix the SAQ assertion at line 183**

In `tests/test_generator.py`, in `test_litestar_generator_saq_rendering`, change:

```python
    assert "saq," in app_content or "plugins=[\n        saq" in app_content
```
to:
```python
    assert "saq" in app_content.lower(), "SAQ plugin reference not found in app.py"
```

This tests that the SAQ plugin is referenced in app.py without being overly specific about formatting.

- [ ] **Step 2: Fix the Dockerfile assertion at line 361**

In `tests/test_generator.py`, in `test_litestar_generator_dockerfile_rendering`, change:

```python
    assert "litestar database upgrade" in content or "alembic upgrade head" in content
```
to:
```python
    has_migration_cmd = "litestar database upgrade" in content or "alembic upgrade head" in content
    assert has_migration_cmd, "No database migration command found in Dockerfile"
```

This evaluates both branches properly and gives a clear error message.

- [ ] **Step 3: Run affected tests**

Run: `pytest tests/test_generator.py::test_litestar_generator_saq_rendering tests/test_generator.py::test_litestar_generator_dockerfile_rendering -v`
Expected: Both PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_generator.py
git commit -m "test: fix weak OR-assertions in test_generator.py"
```

---

### Task 4: Add `spec=` to mocks in `test_cli.py` (#32)

Several `mocker.Mock()` calls in `test_cli.py` lack `spec=` parameter, allowing tests to pass even if they call non-existent methods.

**Files:**
- Modify: `tests/test_cli.py:374,399,423,448,524`
- Modify: `tests/test_vite_lifecycle.py:74`

- [ ] **Step 1: Add import for `LitestarGenerator` in `test_cli.py`**

In `tests/test_cli.py`, add to the imports:

```python
from src.Litestar.generator import LitestarGenerator
```

- [ ] **Step 2: Replace bare `Mock()` with `Mock(spec=LitestarGenerator)` in `test_cli.py`**

Find all occurrences of:
```python
generator._framework_generator = mocker.Mock()
```

Replace each with:
```python
generator._framework_generator = mocker.Mock(spec=LitestarGenerator)
```

These occur in the `TestRunPostGenerationSetup` class at approximately lines 374, 399, 423, 448, and 524.

- [ ] **Step 3: Add `spec=ProjectConfig` to mock in `test_vite_lifecycle.py`**

In `tests/test_vite_lifecycle.py`, at line 74, change:
```python
    config = mocker.Mock()
```
to:
```python
    config = mocker.Mock(spec=ProjectConfig)
```

Also add the import at the top of the file:
```python
from src.models import ProjectConfig
```

- [ ] **Step 4: Run affected tests**

Run: `pytest tests/test_cli.py::TestRunPostGenerationSetup tests/test_vite_lifecycle.py -v`
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_cli.py tests/test_vite_lifecycle.py
git commit -m "test: add spec= to Mock objects for type safety"
```

---

### Task 5: Test `NotImplementedError` for unsupported framework (#29)

`ProjectGenerator.generate()` at `src/generator.py:34-36` raises `NotImplementedError` for unsupported frameworks, but this branch is never tested.

**Files:**
- Modify: `tests/test_project_generator.py`

- [ ] **Step 1: Write the failing test**

Add to the `TestProjectGenerator` class in `tests/test_project_generator.py`:

```python
def test_generate_unsupported_framework_raises(self, tmp_path: Path) -> None:
    """Verify generate raises NotImplementedError for unsupported framework."""
    config = ProjectConfig(
        name="Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=[],
        docker=False,
        docker_infra=False,
    )

    generator = ProjectGenerator(config, tmp_path)
    # Monkeypatch the framework to a value that's not handled
    generator.config = ProjectConfig(
        name="Test",
        framework="UnsupportedFramework",  # type: ignore[arg-type]
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=[],
        docker=False,
        docker_infra=False,
    )

    with pytest.raises(NotImplementedError, match="not yet supported"):
        generator.generate()
```

Also add `import pytest` to the imports if not already present.

- [ ] **Step 2: Run test to verify it passes**

Run: `pytest tests/test_project_generator.py::TestProjectGenerator::test_generate_unsupported_framework_raises -v`
Expected: PASS — the code raises `NotImplementedError` for frameworks != LITESTAR.

- [ ] **Step 3: Commit**

```bash
git add tests/test_project_generator.py
git commit -m "test: add coverage for NotImplementedError on unsupported framework"
```

---

### Task 6: Test `discover_plugins` error branch (#28)

The `except (ImportError, AttributeError): continue` at `src/plugin.py:127` is untested.

**Files:**
- Modify: `tests/test_plugin.py`

- [ ] **Step 1: Write test for `ImportError` in plugin discovery**

Add to the `TestDiscoverPlugins` class in `tests/test_plugin.py`:

```python
def test_discover_plugins_handles_import_error(self, mocker: MockerFixture) -> None:
    """Verify discover_plugins skips plugins that raise ImportError."""
    original_import = importlib.import_module

    def failing_import(name: str):
        if "AdvancedAlchemy" in name:
            raise ImportError("Simulated import failure")
        return original_import(name)

    mocker.patch("importlib.import_module", side_effect=failing_import)

    plugins = discover_plugins("Litestar")

    # Should have fewer plugins since AdvancedAlchemy failed to import
    ids = [p.id for p in plugins]
    assert "advanced_alchemy" not in ids
    # Other plugins should still be discovered
    assert len(plugins) >= 1

def test_discover_plugins_handles_attribute_error(self, mocker: MockerFixture) -> None:
    """Verify discover_plugins skips plugins that raise AttributeError."""
    original_import = importlib.import_module

    def failing_import(name: str):
        if "LitestarSAQ" in name:
            raise AttributeError("Simulated attribute error")
        return original_import(name)

    mocker.patch("importlib.import_module", side_effect=failing_import)

    plugins = discover_plugins("Litestar")

    ids = [p.id for p in plugins]
    assert "litestar_saq" not in ids
    assert len(plugins) >= 1
```

Also add these imports at the top of `tests/test_plugin.py`:

```python
import importlib

from pytest_mock import MockerFixture
```

- [ ] **Step 2: Run the new tests**

Run: `pytest tests/test_plugin.py -k "import_error or attribute_error" -v`
Expected: Both PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_plugin.py
git commit -m "test: add coverage for discover_plugins error handling branches"
```

---

### Task 7: Test `LitestarGenerator.post_generate()` directly (#30)

`LitestarGenerator.post_generate()` at `src/Litestar/generator.py:110-114` iterates enabled plugins and calls their `post_generate`. It's never tested directly (only indirectly through `run_post_generation_setup`).

**Files:**
- Modify: `tests/test_generator.py`

- [ ] **Step 1: Write test for `LitestarGenerator.post_generate()` with no enabled plugins**

Add to `tests/test_generator.py`:

```python
def test_litestar_generator_post_generate_no_plugins(tmp_path: Path) -> None:
    """Verify post_generate does nothing when no plugins are enabled."""
    config = ProjectConfig(
        name="Post Gen Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=[],
        docker=False,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)
    # Should not raise
    generator.post_generate()
```

- [ ] **Step 2: Write test for `LitestarGenerator.post_generate()` with an enabled plugin**

Add to `tests/test_generator.py`:

```python
def test_litestar_generator_post_generate_calls_plugin(tmp_path: Path, mocker) -> None:
    """Verify post_generate calls post_generate on each enabled plugin."""
    config = ProjectConfig(
        name="Post Gen Test",
        framework=Framework.LITESTAR,
        database=Database.POSTGRESQL,
        memory_store=MemoryStore.NONE,
        plugins=["advanced_alchemy"],
        docker=False,
        docker_infra=False,
    )

    generator = LitestarGenerator(config, tmp_path)

    # Mock all discovered plugins' post_generate
    for plugin in generator.plugins:
        mocker.patch.object(plugin, "post_generate")

    generator.post_generate()

    # Verify the enabled plugin's post_generate was called
    for plugin in generator.plugins:
        if config.has_plugin(plugin.id):
            plugin.post_generate.assert_called_once_with(config, tmp_path)
        else:
            plugin.post_generate.assert_not_called()
```

- [ ] **Step 3: Run the new tests**

Run: `pytest tests/test_generator.py -k "post_generate" -v`
Expected: Both PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_generator.py
git commit -m "test: add direct tests for LitestarGenerator.post_generate()"
```

---

### Task 8: Add `LitestarGranianPlugin` direct tests (#35)

`LitestarGranianPlugin` has no dedicated test file. The `LitestarVitePlugin` has `test_vite_lifecycle.py`, and `AdvancedAlchemyPlugin`/`LitestarSAQPlugin` have tests in `test_plugin.py`. Granian needs at least basic property and applicability tests.

**Files:**
- Create: `tests/test_granian_plugin.py`

- [ ] **Step 1: Create `tests/test_granian_plugin.py`**

```python
# ruff: noqa: PLR6301
"""Unit tests for LitestarGranianPlugin."""

from src.Litestar.Plugins.LitestarGranian import LitestarGranianPlugin
from src.models import Database, Framework, MemoryStore, ProjectConfig


class TestLitestarGranianPlugin:
    """Tests for LitestarGranianPlugin."""

    def test_plugin_id(self) -> None:
        """Verify plugin ID is derived correctly from class name."""
        plugin = LitestarGranianPlugin()
        assert plugin.id == "litestar_granian"

    def test_plugin_name(self) -> None:
        """Verify plugin display name."""
        plugin = LitestarGranianPlugin()
        assert plugin.name == "Litestar Granian (Server)"

    def test_plugin_description(self) -> None:
        """Verify plugin description is set."""
        plugin = LitestarGranianPlugin()
        assert "Granian" in plugin.description

    def test_is_applicable_always_true(self) -> None:
        """Verify Granian plugin is always applicable (inherits BasePlugin default)."""
        plugin = LitestarGranianPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert plugin.is_applicable(config) is True

    def test_is_applicable_with_database(self) -> None:
        """Verify Granian plugin is applicable even with database configured."""
        plugin = LitestarGranianPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.POSTGRESQL,
            memory_store=MemoryStore.REDIS,
            plugins=["litestar_granian"],
            docker=True,
            docker_infra=True,
        )
        assert plugin.is_applicable(config) is True

    def test_get_template_context_empty(self) -> None:
        """Verify Granian plugin returns empty template context (inherits default)."""
        plugin = LitestarGranianPlugin()
        config = ProjectConfig(
            name="Test",
            framework=Framework.LITESTAR,
            database=Database.NONE,
            memory_store=MemoryStore.NONE,
            plugins=[],
            docker=False,
            docker_infra=False,
        )
        assert plugin.get_template_context(config) == {}
```

- [ ] **Step 2: Run the new tests**

Run: `pytest tests/test_granian_plugin.py -v`
Expected: All PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_granian_plugin.py
git commit -m "test: add dedicated test file for LitestarGranianPlugin"
```

---

### Task 9: Test `.env.example` copy and `.dockerignore` copy behavior (#36)

The `.env.example` -> `.env` copy and `.gitignore` -> `.dockerignore` copy in `run_post_generation_setup()` need tests for edge cases (files not existing).

**Files:**
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add test for `.env.example` copy**

Add to `TestRunPostGenerationSetup` in `tests/test_cli.py`:

```python
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
        docker_infra=False,
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
        docker_infra=False,
    )
    generator = ProjectGenerator(config, tmp_path)
    generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

    run_post_generation_setup(generator, tmp_path)

    env_file = tmp_path / ".env"
    assert not env_file.exists()
```

- [ ] **Step 2: Add test for skipping `.dockerignore` when docker is False**

Add to `TestRunPostGenerationSetup`:

```python
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
        docker_infra=False,
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
        docker_infra=False,
    )
    generator = ProjectGenerator(config, tmp_path)
    generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

    run_post_generation_setup(generator, tmp_path)

    dockerignore = tmp_path / ".dockerignore"
    assert not dockerignore.exists()
```

- [ ] **Step 3: Run the new tests**

Run: `pytest tests/test_cli.py -k "env_example or env_copy or dockerignore_when_no" -v`
Expected: All PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_cli.py
git commit -m "test: add coverage for .env.example and .dockerignore copy behavior"
```

---

### Task 10: Test subprocess failure paths (#27)

No tests exist for `subprocess.CalledProcessError` from `git init`, `uv sync`, `docker compose`, or `ruff` in `run_post_generation_setup()`.

**Files:**
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add test for `git init` failure**

Add to `TestRunPostGenerationSetup` in `tests/test_cli.py`:

```python
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
        docker_infra=False,
    )
    generator = ProjectGenerator(config, tmp_path)
    generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

    with pytest.raises(sp.CalledProcessError):
        run_post_generation_setup(generator, tmp_path)
```

- [ ] **Step 2: Add test for `uv sync` failure**

Add to `TestRunPostGenerationSetup`:

```python
def test_uv_sync_failure_raises(self, tmp_path: Path, mocker: MockerFixture) -> None:
    """Verify CalledProcessError from uv sync propagates."""
    import subprocess as sp

    call_count = 0

    def selective_fail(*args, **kwargs):  # noqa: ARG001
        nonlocal call_count
        call_count += 1
        if call_count == 2:  # uv sync is the second subprocess call
            raise sp.CalledProcessError(1, ["uv", "sync"])

    mocker.patch("subprocess.run", side_effect=selective_fail)

    config = ProjectConfig(
        name="Test",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=[],
        docker=False,
        docker_infra=False,
    )
    generator = ProjectGenerator(config, tmp_path)
    generator._framework_generator = mocker.Mock(spec=LitestarGenerator)

    with pytest.raises(sp.CalledProcessError):
        run_post_generation_setup(generator, tmp_path)
```

- [ ] **Step 3: Run the new tests**

Run: `pytest tests/test_cli.py -k "failure_raises" -v`
Expected: Both PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_cli.py
git commit -m "test: add coverage for subprocess failure paths in post-generation setup"
```

---

### Task 11: Test `main()` CLI flow (#26)

`main()` at `src/cli.py:272-348` has zero test coverage. It orchestrates all `ask_*` functions and generation.

**Files:**
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add import for `main` in `tests/test_cli.py`**

Update the import block to include `main`:

```python
from src.cli import (
    ask_database,
    ask_docker,
    ask_framework,
    ask_memory_store,
    ask_plugins,
    ask_project_name,
    main,
    run_post_generation_setup,
)
```

- [ ] **Step 2: Write test for `main()` happy path**

Add a new class to `tests/test_cli.py`:

```python
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
        mocker.patch("src.cli.ask_docker", return_value=(False, False))

        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = True  # Confirm generation

        mock_generator_cls = mocker.patch("src.cli.ProjectGenerator")
        mock_generator = mock_generator_cls.return_value

        # Mock Path.cwd() to use tmp_path
        mocker.patch("src.cli.Path.cwd", return_value=tmp_path)

        mock_post_gen = mocker.patch("src.cli.run_post_generation_setup")

        main()

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
        mocker.patch("src.cli.ask_docker", return_value=(False, False))

        mock_confirm = mocker.patch("questionary.confirm")
        mock_confirm.return_value.ask.return_value = False  # Decline

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    def test_main_keyboard_interrupt(self, mocker: MockerFixture) -> None:
        """Verify main() handles KeyboardInterrupt gracefully."""
        mocker.patch("src.cli.print_banner")
        mocker.patch("src.cli.ask_project_name", side_effect=KeyboardInterrupt)

        # Should not raise — main() catches KeyboardInterrupt
        main()
```

- [ ] **Step 3: Run the new tests**

Run: `pytest tests/test_cli.py::TestMain -v`
Expected: All PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_cli.py
git commit -m "test: add coverage for main() CLI entry point"
```

---

### Task 12: Rename `test_generator.py` to `test_litestar_generator.py` (#33)

`tests/test_generator.py` tests `LitestarGenerator`, not `ProjectGenerator` (which is tested in `test_project_generator.py`). The name is misleading.

**Files:**
- Rename: `tests/test_generator.py` -> `tests/test_litestar_generator.py`

- [ ] **Step 1: Rename the file**

```bash
git mv tests/test_generator.py tests/test_litestar_generator.py
```

- [ ] **Step 2: Run full test suite to verify nothing breaks**

Run: `pytest -v`
Expected: All tests PASS. pytest discovers tests by filename pattern `test_*.py`, so the rename is transparent.

- [ ] **Step 3: Commit**

```bash
git add tests/
git commit -m "refactor: rename test_generator.py to test_litestar_generator.py for clarity"
```
