# Litestar Start

**Litestar Start** is an interactive CLI tool designed to scaffold production-ready fullstack applications with modular choices. It combines modern python tooling with established patterns to get you up and running quickly.

## Features

*   **Interactive CLI**: Beautiful terminal interface using `rich` and `questionary`.
*   **Backend Frameworks**:
    *   [Litestar](https://litestar.dev/)
    *   [FastAPI](https://fastapi.tiangolo.com/)
*   **Frontend Frameworks**:
    *   [React](https://react.dev/)
*   **Database Support**:
    *   PostgreSQL
    *   MySQL
    *   SQLite
    *   MongoDB
*   **ORM Integration**:
    *   [SQLAlchemy](https://www.sqlalchemy.org/)
*   **Tooling**:
    *   Docker & Docker Compose support
    *   GitHub Actions CI/CD workflows
    *   Ruff & Pre-commit linting configuration

## Installation

You can install and run `litestar-start` using `uvx` or `pipx`:

```bash
uvx litestar-start

# or

pipx run litestar-start
```

## Usage

Simply run the command and follow the interactive prompts:

```bash
litestar-start
```

You will be asked to configure:
1.  **Project Details**: Name and description.
2.  **Tech Stack**: Backend, Frontend, Database, ORM.
3.  **Features**: Docker, CI/CD, Testing, Linting.

## Contributing

We welcome contributions! Whether it's adding a new framework, fixing a bug, or improving documentation.

Please read our [Developer Guide](DEVELOPMENT.md) to get started with setting up the project locally.

## License

MIT
