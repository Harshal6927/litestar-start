# Litestar Start - Project Context

## Overview
`litestar-start` is an interactive Command Line Interface (CLI) tool designed to scaffold production-ready Litestar backend projects. It allows developers to quickly generate project structures with optional configurations for databases (SQLAlchemy) and authentication (JWT), using Docker for containerization.

## Architecture
The project follows a modular architecture to support extensibility (e.g., adding new frameworks or plugins):

1.  **CLI (`src/cli.py`)**: The entry point using `questionary` for prompts and `rich` for output. It collects user choices into a `ProjectConfig` model.
2.  **Generator (`src/generator.py`)**: Orchestrates the generation process, delegating to framework-specific generators.
3.  **Models (`src/models.py`)**: Uses `msgspec` to define strict data models for project configuration (`ProjectConfig`, `DatabaseConfig`, etc.).
4.  **Templates (`src/Litestar/`)**: Contains Jinja2 templates for the Litestar framework, organized by component (`App`, `Config`, `Containers`, `Plugins`).

## Key Files & Directories

*   `src/cli.py`: Main entry point for the CLI.
*   `src/generator.py`: Core logic for orchestrating project generation.
*   `src/Litestar/`: Contains Litestar-specific generator logic and Jinja2 templates.
    *   `app/`: Core application structure.
    *   `Config/`: Project config files (`pyproject.toml`, `.env`, etc.).
    *   `Plugins/`: Optional add-ons like SQLAlchemy and JWT.
*   `tools/prepare_release.py`: Script for release preparation.
*   `pyproject.toml`: Project configuration, dependencies, and build system (Hatchling).
*   `Makefile`: specific commands for linting and releasing.

## Development Workflow

### Prerequisites
*   Python >= 3.13
*   `uv` (Package manager)

### Installation & Setup
To install dependencies:
```bash
uv sync
```

### Running the CLI
To run the CLI locally during development:
```bash
uv run litestar-start
```
Or directly via the module:
```bash
uv run python -m src.cli
```

### Linting & Code Quality
The project uses `pre-commit`, `ruff`, and `ty` for quality checks.
To run all linters:
```bash
make lint
```
This command installs pre-commit hooks, runs them, and executes type checks.

### Releasing
To prepare a release:
```bash
make release
```
This runs the preparation script and syncs/locks dependencies.

## Conventions

*   **Templating**: All scaffolded files are Jinja2 templates (`.jinja`).
*   **Models**: Use `msgspec.Struct` for internal data structures.
*   **Style**: Adhere to `ruff` configuration in `pyproject.toml` (line length 120).
*   **Typing**: Strict type hints are enforced (checked via `ty`).
*   **Plugins**: New features should be implemented as plugins within the `src/<Framework>/Plugins` directory structure.
