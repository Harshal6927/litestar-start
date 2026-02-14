# Agent Guidelines for litestar-start

This document contains instructions for AI agents operating in this repository.
`litestar-start` is an interactive CLI tool for scaffolding fullstack projects, built with Python 3.13+.

## 1. Environment & Dependency Management

This project uses `uv` for fast dependency management and `hatchling` for building.

- **Install dependencies:**
  ```bash
  uv sync
  ```
- **Update lockfile:**
  ```bash
  uv lock
  ```
- **Run commands in venv:**
  Use `uv run <command>` (e.g., `uv run pytest`) or activate the virtualenv:
  ```bash
  source .venv/bin/activate
  ```

## 2. Build, Lint, and Test Commands

### Testing
The project uses `pytest` and `pytest-mock`.

- **Run all tests:**
  ```bash
  pytest
  ```
- **Run a single test file:**
  ```bash
  pytest tests/test_generator.py
  ```
- **Run a specific test case:**
  ```bash
  pytest tests/test_generator.py::test_function_name
  ```
- **Run with verbose output:**
  ```bash
  pytest -v
  ```
- **Run tests matching a keyword expression:**
  ```bash
  pytest -k "docker or database"
  ```

### Linting and Formatting
Strict code quality is enforced using `ruff`, `ty`, and `pre-commit`.

- **Run all linters (Recommended):**
  ```bash
  make lint
  ```
  *Note: This runs `ruff check --fix`, `ty check`, and `pre-commit run -a`.*

- **Run Ruff manually:**
  ```bash
  ruff check .
  ```
  *Note: The following rules are ignored in `pyproject.toml`: `CPY001`, `D100`, `D104`, `PLC0415`, `PLR0911`, `S101`, `SLF001`, `RUF067`.*

- **Run Type Checking:**
  ```bash
  ty check
  ```

### Release
- **Prepare a new release:**
  ```bash
  make release
  ```
  *This script bumps versions in `pyproject.toml` and `src/__init__.py`, then updates the lockfile.*

## 3. Code Style Guidelines

Adhere strictly to the following conventions to match the existing codebase.

### General
- **Python Version:** Target Python 3.13+.
- **Line Length:** 120 characters.
- **File Operations:** ALWAYS use `pathlib.Path` instead of `os.path` strings.
- **CLI Output:** Use `rich` for console output and `questionary` for user prompts.

### Data Structures
- **Data Models:** Use `msgspec.Struct` for defining data structures and configurations.
  *   **DO NOT** use `dataclasses` or `pydantic`.
- **Enums:** Use `enum.StrEnum` for string-based enumerations.

### Imports
- **Sorting:** Imports are sorted automatically by Ruff.
- **Grouping:**
  1. Standard library (e.g., `pathlib`, `re`)
  2. Third-party libraries (e.g., `jinja2`, `msgspec`, `rich`)
  3. Local application imports (e.g., `src.utils`)

### Typing
- **Strict Typing:** All functions and methods must have type annotations for arguments and return values.
- **Unions:** Use the `|` operator (e.g., `str | None`) instead of `Optional` or `Union`.
- **Collections:** Use built-in types (`list`, `dict`, `set`, `tuple`) instead of `typing.List`, etc.

### Naming Conventions
- **Variables/Functions:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `SCREAMING_SNAKE_CASE`
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
- Use specific exceptions where possible.
- Avoid bare `except:` blocks.

## 4. Directory Structure

- `src/`: Source code.
  - `cli.py`: Main entry point.
  - `models.py`: Configuration data models (`msgspec`).
  - `generator.py`: Project generation logic.
  - `plugin.py`: Plugin system logic.
- `tests/`: Test files (mirrors source structure).
- `tools/`: Maintenance scripts (e.g., `prepare_release.py`).
