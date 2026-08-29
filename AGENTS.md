# Agent Guidelines for litestar-start

`litestar-start` is an interactive CLI tool for scaffolding fullstack projects, built with Python 3.13+.

## 1. Environment & Dependency Management

This project uses `uv` for fast dependency management and `hatchling` for building.

- **Install dependencies:** `uv sync`
- **Update lockfile:** `uv lock`
- **Run commands in venv:** Use `uv run <command>` (e.g., `uv run pytest`).

## 2. Build, Lint, and Test Commands

### Testing
The project uses `pytest` and `pytest-mock`.

- **Run all tests:** `pytest`
- **Run a specific test:** `pytest tests/test_generator.py::test_function_name`
- **Run with keyword filter:** `pytest -k "docker or database"`

### Linting and Formatting
Strict code quality is enforced using `ruff`, `ty`, and `pre-commit`.

- **Run all linters (Recommended):** `make lint`
  *Runs `ruff check --fix`, `ty check`, and `pre-commit run -a`.*
- **Run Ruff manually:** `ruff check .`
- **Run Type Checking:** `ty check`

### Release
- **Prepare a new release:** `make release`

## 3. Code Style Guidelines

### General
- **File Operations:** ALWAYS use `pathlib.Path` instead of `os.path` strings.
- **CLI Output:** Use `rich` for console output and `questionary` for user prompts.

### Data Structures
- **Data Models:** Use `msgspec.Struct` for defining data structures and configurations.
  *   **DO NOT** use `dataclasses` or `pydantic`.
- **Enums:** Use `enum.StrEnum` for string-based enumerations.

### Typing
- **Strict Typing:** All functions and methods must have type annotations for arguments and return values.

### Naming Conventions
- **Private Members:** Prefix with `_`. Note that `SLF001` (private access) is ignored by linter, but prefer public interfaces where possible.

### Docstrings
- Use **Google-style** docstrings for all public modules, functions, classes, and methods.
- **Do not** add docstrings to `__init__.py` files (rule `RUF067`).
- Format:
  ```python
  def function(arg: int) -> str:
      """Short summary of the function.

      Args:
          arg: Description of the argument.

      Returns:
          Description of the return value.

      """
  ```

### Error Handling
- Validate inputs early (fail fast).

## 4. Directory Structure

- `src/`: Source code.
  - `cli.py`: Main entry point.
  - `models.py`: Configuration data models (`msgspec`).
  - `generator.py`: Project generation logic.
  - `plugin.py`: Plugin system logic.
- `tests/`: Test files (mirrors source structure).
- `tools/`: Maintenance scripts (e.g., `prepare_release.py`).
