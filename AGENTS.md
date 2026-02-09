# Agent Guidelines for litestar-start

This document contains instructions for AI agents operating in this repository.

## 1. Build, Lint, and Test Commands

This project uses `uv` for dependency management and `hatchling` for building.

### Dependency Management
- **Install dependencies:** `uv sync`
- **Update lockfile:** `uv lock` (or `uv lock --upgrade` to upgrade)

### Testing
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

### Linting and Formatting
- **Run all linters (Ruff, Type Checking, Pre-commit):**
  ```bash
  make lint
  ```
  *Note: This runs `ruff check --fix`, `ty check`, and `pre-commit run -a`.*

- **Run Ruff manually:**
  ```bash
  ruff check .
  ```

- **Run Type Checking manually:**
  ```bash
  ty check
  ```

## 2. Code Style Guidelines

Adhere strictly to the following conventions to match the existing codebase.

### General
- **Python Version:** Target Python 3.13+.
- **Line Length:** 120 characters (configured in `pyproject.toml`).
- **File Operations:** Always use `pathlib.Path` instead of `os.path` strings.
- **Data Models:** Use `msgspec.Struct` for defining data structures/configurations, not `dataclasses` or `pydantic`.
- **Enums:** Use `enum.StrEnum` for string-based enumerations.

### Imports
- Group imports:
  1. Standard library (e.g., `pathlib`, `re`)
  2. Third-party libraries (e.g., `jinja2`, `msgspec`)
  3. Local application imports (e.g., `src.utils`)
- Imports are sorted automatically by Ruff; attempt to group them logically.

### Typing
- **Strict Typing:** All functions and methods must have type annotations for arguments and return values.
- Use built-in types (`list`, `dict`, `set`) instead of `typing.List`, etc.
- Use `|` for unions (e.g., `str | None`) instead of `Optional` or `Union`.

### Naming Conventions
- **Variables/Functions:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `SCREAMING_SNAKE_CASE`
- **Private Members:** Prefix with `_` (though `SLF001` is ignored in Ruff, still prefer public interfaces).

### Docstrings
- Use **Google-style** docstrings for all public modules, functions, classes, and methods.
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

### Directory Structure
- `src/`: Source code.
- `tests/`: Test files (mirrors source structure or flat list).
- `tools/`: Build and maintenance scripts.
