# Litestar Start

This document explains the architecture and design of `litestar-start`, a CLI tool for scaffolding Litestar projects.

## Overview

`litestar-start` is an interactive CLI tool that helps developers quickly scaffold new Litestar projects with optional plugins like AdvancedAlchemy ORM.

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
    │   └── docker-compose.dev-infra.yml.jinja
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

## Core Components

### 1. CLI (`cli.py`)

The CLI is the entry point for the tool. It uses:
- **questionary** - For interactive prompts
- **rich** - For beautiful console output

**Flow:**
1. Display welcome banner
2. Ask for project name
3. Ask for backend framework (currently only Litestar)
4. Ask for database choice
5. Ask for plugins (based on database choice)
6. Ask for Docker configuration
7. Display summary and confirm
8. Generate project

### 2. Models (`models.py`)

Uses **msgspec** for efficient data serialization. Key models:

- **Framework** - Enum of supported frameworks (Litestar, future: FastAPI)
- **Database** - Enum of database options (PostgreSQL, SQLite, MySQL, None)
- **MemoryStore** - Enum of memory store options (Redis, Valkey, None)
- **ProjectConfig** - Main configuration struct containing all user choices
- **DatabaseConfig** - Database-specific configuration (driver, port, URL)

### 3. Generator (`generator.py`)

The orchestrator that delegates to framework-specific generators. Currently supports:
- `LitestarGenerator` - Generates Litestar projects

### 4. Litestar Generator (`Litestar/generator.py`)

Handles the actual file generation:

1. **Config Files** - Generates `pyproject.toml`, `.gitignore`, `.env.example`, `README.md`
2. **Base Application** - Generates core `app/` directory with main.py, config.py
3. **Plugins** - Generates plugin-specific files (db/, auth/) if selected
4. **Containers** - Generates Docker files if requested

### 5. Templates

All templates use **Jinja2** with `.jinja` extension. Template context includes:
- `project_name` - Human-readable name
- `project_slug` - Python-safe name
- `database` - Selected database enum
- `advanced_alchemy` - Boolean flag
- `docker` - Boolean flag

## Adding New Features

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
   from src.models import ProjectConfig
   from src.plugin import BasePlugin


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

### Adding a New Framework

1. Create framework directory:
   ```
   src/NewFramework/
   ├── __init__.py
   ├── generator.py
   ├── App/
   ├── Config/
   ├── Containers/
   └── Plugins/
   ```

2. Add to `Framework` enum in `models.py`

3. Create `NewFrameworkGenerator` class in `generator.py`

4. Update main `generator.py` to handle the new framework

5. Update CLI to enable the framework option

### Adding a New Database

1. Add to `Database` enum in `models.py`

2. Add configuration in `DatabaseConfig.for_database()`:
   ```python
   Database.NEW_DB: cls(
       driver="newdb+async",
       port=1234,
       default_url="newdb+async://...",
       docker_image="newdb:latest",
   )
   ```

3. Update templates that reference database configuration

## Template Rendering

Templates are rendered using Jinja2 with these settings:
- `trim_blocks=True` - Removes first newline after block tag
- `lstrip_blocks=True` - Strips leading whitespace from block lines
- `keep_trailing_newline=True` - Preserves trailing newlines

### Template Context Variables

| Variable | Type | Description |
|----------|------|-------------|
| `project` | `ProjectConfig` | Full project configuration |
| `project_name` | `str` | Human-readable project name |
| `project_slug` | `str` | Python-safe name |
| `database` | `Database` | Selected database enum |
| `db_config` | `DatabaseConfig` | Database configuration |
| `advanced_alchemy` | `bool` | AdvancedAlchemy plugin enabled |
| `has_database` | `bool` | Any database selected |
| `docker` | `bool` | Dockerfile requested |
| `docker_dev_infra` | `bool` | Dev infra compose requested |

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
└── docker-compose.dev-infra.yml  # If Docker dev infra selected
```

## Dependencies

- **questionary** - Interactive CLI prompts
- **rich** - Terminal formatting and output
- **jinja2** - Template rendering
- **msgspec** - Fast data serialization

## Future Improvements

- [ ] Add FastAPI framework support
- [ ] Add more plugins (Structlog, CORS)
- [ ] Add test scaffolding for generated projects
- [ ] Add CI workflow for generated projects
