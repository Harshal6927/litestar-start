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
- **Docker** — optional Dockerfile and `docker-compose.dev-infra.yml` for local development
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
