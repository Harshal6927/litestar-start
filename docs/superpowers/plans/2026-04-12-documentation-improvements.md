# Documentation Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix stale documentation, add missing docstrings, expand README, and add `__all__` exports to all public modules (audit items #39-43).

**Architecture:** Update documentation files and source code in-place. Each task is a focused change: README expansion, CONTRIBUTING.md fix, plugin docstrings, `_render_templates` docstring, and `__all__` exports. No behavioral changes — documentation only.

**Tech Stack:** Python 3.13+, ruff (linting), Markdown

---

## File Map

- Modify: `README.md` — expand from 9 lines to include features, usage examples, plugin descriptions
- Modify: `CONTRIBUTING.md` — fix stale references to nonexistent directories and outdated instructions
- Modify: `src/Litestar/Plugins/AdvancedAlchemy/__init__.py` — add docstrings (remove `# noqa: D102`)
- Modify: `src/Litestar/Plugins/LitestarSAQ/__init__.py` — add docstrings (remove `# noqa: D102`)
- Modify: `src/Litestar/Plugins/LitestarVite/__init__.py` — add docstrings (remove `# noqa: D102`)
- Modify: `src/Litestar/generator.py:64-71` — expand `_render_templates` docstring
- Modify: `src/models.py` — add `__all__`
- Modify: `src/plugin.py` — add `__all__`
- Modify: `src/utils.py` — add `__all__`
- Modify: `src/cli.py` — add `__all__`

---

### Task 1: Expand `README.md` (#39)

Current README is only 9 lines with no feature list, usage examples, or plugin descriptions.

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace `README.md` content**

Replace the entire file with:

```markdown
# Litestar Start

Interactive CLI to scaffold fullstack [Litestar](https://litestar.dev) projects with modular choices.

## Features

- **Interactive prompts** — guided setup with [questionary](https://questionary.readthedocs.io/)
- **Database support** — PostgreSQL, MySQL, or SQLite via AdvancedAlchemy
- **Memory stores** — Redis or Valkey for caching / background tasks
- **Plugin system** — modular plugins that add functionality:
  - **AdvancedAlchemy** — SQLAlchemy ORM integration with models, services, and dependencies
  - **Litestar SAQ** — background task queue powered by SAQ (requires a memory store)
  - **Litestar Vite** — frontend asset bundling with Vite
  - **Litestar Granian** — high-performance Granian ASGI server
- **Docker** — optional Dockerfile and `docker-compose.infra.yml` for local development
- **Post-generation setup** — automatic `git init`, `uv sync`, Docker infrastructure startup, and import sorting

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (used for dependency management in generated projects)

## Installation

```bash
uvx litestar-start
```

Or install globally:

```bash
uv tool install litestar-start
```

## Usage

Run the CLI and follow the interactive prompts:

```bash
litestar-start
```

You will be asked to:

1. Enter a project name
2. Select a database (PostgreSQL, SQLite, MySQL, or None)
3. Select a memory store (Redis, Valkey, or None)
4. Choose plugins (based on your database/store choices)
5. Configure Docker options
6. Confirm and generate

The generated project includes a working Litestar application with your selected options pre-configured.

## Development

```bash
git clone https://github.com/Harshal6927/litestar-start.git
cd litestar-start
uv sync
```

Run tests:

```bash
pytest
```

Run linters:

```bash
make lint
```

## License

MIT
```

- [ ] **Step 2: Verify README renders correctly**

Review the file manually. No automated check needed for Markdown content.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: expand README with features, usage, and development instructions"
```

---

### Task 2: Fix stale `CONTRIBUTING.md` (#40)

`CONTRIBUTING.md` references nonexistent directories (`SQLAlchemy/`, `JWT/`), shows wrong generated project structure, and has outdated Plugin enum instructions.

**Files:**
- Modify: `CONTRIBUTING.md`

- [ ] **Step 1: Fix the project structure tree**

In `CONTRIBUTING.md`, replace the project structure section (lines 11-50) with the actual structure:

```markdown
## Project Structure

```
src/
├── __init__.py          # Package metadata and version
├── cli.py               # Main CLI entry point with questionary prompts
├── generator.py         # Project generator orchestrator
├── models.py            # Data models using msgspec
├── utils.py             # Utility functions (templating, validation)
└── Litestar/            # Litestar framework templates
    ├── __init__.py
    ├── generator.py     # Litestar-specific generation logic
    ├── Config/          # Project configuration templates
    │   ├── pyproject.toml.jinja
    │   ├── gitignore.jinja
    │   ├── env.example.jinja
    │   └── readme.md.jinja
    ├── App/             # Core application templates
    │   └── *.jinja
    ├── Containers/      # Docker templates
    │   ├── Dockerfile.jinja
    │   ├── docker-compose.yml.jinja
    │   └── docker-compose.infra.yml.jinja
    └── Plugins/         # Optional plugin templates
        ├── __init__.py
        ├── AdvancedAlchemy/
        │   ├── __init__.py
        │   └── Templates/
        ├── LitestarSAQ/
        │   ├── __init__.py
        │   └── Templates/
        ├── LitestarVite/
        │   ├── __init__.py
        │   └── Templates/
        └── LitestarGranian/
            └── __init__.py
```
```

- [ ] **Step 2: Fix the Plugin enum instructions**

Replace the "Adding a New Plugin" section (around lines 104-128) with updated instructions that reflect the current plugin system (no `Plugin` enum — plugins are auto-discovered classes):

```markdown
### Adding a New Plugin

1. Create plugin directory under the framework's `Plugins/` directory:
   ```
   src/Litestar/Plugins/NewPlugin/
   ├── __init__.py
   └── Templates/
       └── *.jinja
   ```

2. In `__init__.py`, create a class that extends `BasePlugin`:
   ```python
   from src.plugin import BasePlugin
   from src.models import ProjectConfig

   class NewPlugin(BasePlugin):
       """Description of the plugin."""

       @property
       def name(self) -> str:
           """Get the plugin display name."""
           return "New Plugin"

       @property
       def description(self) -> str:
           """Get the plugin description."""
           return "Description for the CLI"

       def is_applicable(self, config: ProjectConfig) -> bool:
           """Check if this plugin is applicable."""
           return True  # or check config fields
   ```

3. The plugin will be automatically discovered by `discover_plugins()`. No enum or CLI changes are needed.

4. Add Jinja2 templates in the `Templates/` subdirectory. They will be rendered into `src/backend/` of the generated project.
```

- [ ] **Step 3: Fix the Models section**

In the Models section (around lines 72-78), replace the `Plugin` enum reference:

Change:
```markdown
- **Plugin** - Enum of available plugins (SQLAlchemy, JWT)
```
to:
```markdown
- **MemoryStore** - Enum of memory store options (Redis, Valkey, None)
```

- [ ] **Step 4: Fix the generated project structure**

Replace the "Generated Project Structure" section (around lines 188-212) with:

```markdown
## Generated Project Structure

A typical generated project looks like:

```
my_project/
├── src/
│   └── backend/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       ├── models/          # If AdvancedAlchemy selected
│       │   └── users.py
│       └── lib/             # If plugins are selected
│           ├── dependencies.py
│           ├── services.py
│           └── tasks.py     # If SAQ selected
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── Dockerfile             # If Docker selected
├── docker-compose.yml     # If Docker selected
└── docker-compose.infra.yml  # If Docker infra selected
```
```

- [ ] **Step 5: Fix the Future Improvements section**

Replace the stale future improvements with accurate ones:

```markdown
## Future Improvements

- [ ] Add FastAPI framework support
- [ ] Add more plugins (Structlog, CORS)
- [ ] Add test scaffolding for generated projects
- [ ] Add CI workflow for generated projects
```

- [ ] **Step 6: Verify lint passes**

Run: `make lint`
Expected: No Markdown-related lint errors.

- [ ] **Step 7: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs: fix stale references and outdated instructions in CONTRIBUTING.md"
```

---

### Task 3: Add docstrings to plugin methods (#41)

Three plugin files suppress docstring warnings with `# noqa: D102` instead of providing actual docstrings. Fix by adding Google-style docstrings and removing the noqa comments.

**Files:**
- Modify: `src/Litestar/Plugins/AdvancedAlchemy/__init__.py`
- Modify: `src/Litestar/Plugins/LitestarSAQ/__init__.py`
- Modify: `src/Litestar/Plugins/LitestarVite/__init__.py`

- [ ] **Step 1: Add docstrings to `AdvancedAlchemyPlugin`**

Replace `src/Litestar/Plugins/AdvancedAlchemy/__init__.py` content with:

```python
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
```

- [ ] **Step 2: Add docstrings to `LitestarSAQPlugin`**

Replace `src/Litestar/Plugins/LitestarSAQ/__init__.py` content with:

```python
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
```

- [ ] **Step 3: Add docstrings to `LitestarVitePlugin`**

In `src/Litestar/Plugins/LitestarVite/__init__.py`, replace the property definitions:

Change `name` property from:
```python
    @property
    def name(self) -> str:  # noqa: D102
        return "Litestar Vite (Frontend Integration)"
```
to:
```python
    @property
    def name(self) -> str:
        """Get the plugin display name.

        Returns:
            The display name shown in the CLI.

        """
        return "Litestar Vite (Frontend Integration)"
```

Change `description` property from:
```python
    @property
    def description(self) -> str:  # noqa: D102
        return "Vite integration for frontend assets in Litestar"
```
to:
```python
    @property
    def description(self) -> str:
        """Get the plugin description.

        Returns:
            A short description of the plugin.

        """
        return "Vite integration for frontend assets in Litestar"
```

- [ ] **Step 4: Run linter to verify noqa comments are no longer needed**

Run: `ruff check src/Litestar/Plugins/ --select D102`
Expected: No D102 violations. The noqa comments have been removed and replaced with actual docstrings.

- [ ] **Step 5: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS. Docstring changes don't affect behavior.

- [ ] **Step 6: Commit**

```bash
git add src/Litestar/Plugins/
git commit -m "docs: add proper docstrings to plugin methods, remove noqa D102 suppression"
```

---

### Task 4: Expand `_render_templates` docstring (#42)

`_render_templates` in `src/Litestar/generator.py:64-71` has a one-line docstring but 5 parameters with no documentation.

**Files:**
- Modify: `src/Litestar/generator.py:64-72`

- [ ] **Step 1: Replace the docstring**

In `src/Litestar/generator.py`, change the `_render_templates` method docstring from:

```python
    def _render_templates(
        self,
        template_dir: Path,
        output_subdir: Path,
        env: Environment,
        context: dict,
        root_template_dir: Path | None = None,
    ) -> None:
        """Recursively render templates from a directory."""
```

to:

```python
    def _render_templates(
        self,
        template_dir: Path,
        output_subdir: Path,
        env: Environment,
        context: dict,
        root_template_dir: Path | None = None,
    ) -> None:
        """Recursively render Jinja2 templates from a directory into the output.

        Walks `template_dir`, rendering every `*.jinja` file with the given
        context and writing the result (sans `.jinja` suffix) into `output_subdir`.
        Subdirectories are traversed recursively.

        Args:
            template_dir: Directory containing `.jinja` template files.
            output_subdir: Target directory where rendered files are written.
            env: The Jinja2 environment used for template loading.
            context: Template variables passed to each render call.
            root_template_dir: The root of the template tree, used to compute
                template names relative to the Jinja2 loader. Defaults to
                `template_dir` on first call and is preserved during recursion.

        """
```

- [ ] **Step 2: Run linter**

Run: `ruff check src/Litestar/generator.py`
Expected: No new lint errors.

- [ ] **Step 3: Commit**

```bash
git add src/Litestar/generator.py
git commit -m "docs: expand _render_templates docstring with Args documentation"
```

---

### Task 5: Add `__all__` to public modules (#43)

`models.py`, `plugin.py`, `utils.py`, and `cli.py` have no `__all__`, making the public API implicit.

**Files:**
- Modify: `src/models.py`
- Modify: `src/plugin.py`
- Modify: `src/utils.py`
- Modify: `src/cli.py`

- [ ] **Step 1: Add `__all__` to `src/models.py`**

After the imports (after `import msgspec`, before the `Framework` class), add:

```python
__all__ = [
    "Database",
    "DatabaseConfig",
    "Framework",
    "MemoryStore",
    "MemoryStoreConfig",
    "ProjectConfig",
]
```

- [ ] **Step 2: Add `__all__` to `src/plugin.py`**

After the imports (after `from src.models import ProjectConfig`, before `def camel_to_snake`), add:

```python
__all__ = [
    "BasePlugin",
    "Plugin",
    "camel_to_snake",
    "discover_plugins",
]
```

- [ ] **Step 3: Add `__all__` to `src/utils.py`**

After the imports (after the jinja2 imports, before `MIN_PROJECT_NAME_LENGTH`), add:

```python
__all__ = [
    "get_package_dir",
    "get_template_env",
    "slugify",
    "validate_project_name",
    "write_file",
]
```

Note: `create_directory` and `render_template` are excluded because they are being removed in the dead-code-cleanup plan. If this plan runs first, include them and they will be removed later. If the dead-code plan runs first, this list is already correct.

- [ ] **Step 4: Add `__all__` to `src/cli.py`**

After the imports (after `from src.utils import validate_project_name`, before `console = Console()`), add:

```python
__all__ = [
    "ask_database",
    "ask_docker",
    "ask_framework",
    "ask_memory_store",
    "ask_plugins",
    "ask_project_name",
    "main",
    "run_post_generation_setup",
]
```

- [ ] **Step 5: Run linter**

Run: `ruff check src/models.py src/plugin.py src/utils.py src/cli.py`
Expected: No new lint errors.

- [ ] **Step 6: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS. `__all__` does not affect runtime behavior.

- [ ] **Step 7: Commit**

```bash
git add src/models.py src/plugin.py src/utils.py src/cli.py
git commit -m "docs: add __all__ exports to all public modules"
```
