# Tech Stack

## Core Technologies
- **Language:** Python 3.13 (utilizing the latest features and strict typing).
- **Dependency & Package Management:** [uv](https://github.com/astral-sh/uv) for fast, reliable dependency resolution and project management.
- **Build System:** [hatchling](https://hatch.pypa.io/latest/) for building and distributing the package.

## CLI & Interaction
- **Prompting:** [questionary](https://github.com/tmbo/questionary) for building the interactive user prompts.
- **Output & Formatting:** [rich](https://github.com/Textualize/rich) for beautiful, formatted terminal output, tables, and progress indicators.

## Core Logic & Generation
- **Templating:** [Jinja2](https://jinja.palletsprojects.com/) for generating the project structure from templates.
- **Data Modeling:** [msgspec](https://github.com/jcrist/msgspec) for high-performance JSON/struct validation and serialization of project configurations.

## Development & Quality Tools
- **Linting & Formatting:** [Ruff](https://github.com/astral-sh/ruff) for fast Python linting and code formatting.
- **Type Checking:** [ty](https://github.com/vrsat-sh/ty) (wrapping mypy/pyright) for enforcing strict type safety.
- **Git Hooks:** [pre-commit](https://pre-commit.com/) to automate quality checks before every commit.
- **Testing:** [pytest](https://pytest.org/) (implied for a project of this scale).

## Scaffolding Target
- **Primary Framework:** [Litestar](https://litestar.dev/) (Production-ready, highly performant ASGI framework).
