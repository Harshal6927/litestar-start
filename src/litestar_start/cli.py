import sys
from typing import Any

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from litestar_start.generator import generate_project

console = Console()


def get_choices() -> dict[str, list[dict[str, str]]]:
    """Define all available choices for each component.

    Returns:
        Dictionary mapping component names to their available choices.

    """
    return {
        "backend": [
            {"name": "FastAPI - Modern, fast Python web framework", "value": "fastapi"},
            {"name": "Django - Full-featured web framework with batteries included", "value": "django"},
            {"name": "Flask - Lightweight and flexible micro-framework", "value": "flask"},
            {"name": "Litestar - High-performance ASGI framework", "value": "litestar"},
        ],
        "frontend": [
            {"name": "React - Popular UI library with large ecosystem", "value": "react"},
            {"name": "Vue - Progressive JavaScript framework", "value": "vue"},
            {"name": "Svelte - Compile-time reactive framework", "value": "svelte"},
            {"name": "None - Backend only (API)", "value": "none"},
        ],
        "database": [
            {"name": "PostgreSQL - Powerful open-source relational database", "value": "postgresql"},
            {"name": "MySQL - Popular relational database", "value": "mysql"},
            {"name": "SQLite - Lightweight file-based database", "value": "sqlite"},
            {"name": "MongoDB - NoSQL document database", "value": "mongodb"},
        ],
        "orm": [
            {"name": "SQLAlchemy - Python SQL toolkit and ORM", "value": "sqlalchemy"},
            {"name": "Tortoise ORM - Easy async ORM for Python", "value": "tortoise"},
            {"name": "Prisma - Next-generation ORM with type safety", "value": "prisma"},
            {"name": "None - Raw SQL queries", "value": "none"},
        ],
        "auth": [
            {"name": "JWT - Stateless token-based authentication", "value": "jwt"},
            {"name": "Session - Traditional server-side sessions", "value": "session"},
            {"name": "OAuth2 - Third-party authentication (Google, GitHub, etc.)", "value": "oauth2"},
            {"name": "None - No authentication", "value": "none"},
        ],
        "features": [
            {"name": "Docker - Containerization with docker-compose", "value": "docker"},
            {"name": "CI/CD - GitHub Actions workflow", "value": "cicd"},
            {"name": "Testing - Pytest setup with fixtures", "value": "testing"},
            {"name": "Linting - Ruff + pre-commit hooks", "value": "linting"},
        ],
    }


def display_banner() -> None:
    """Display the welcome banner."""
    banner = Text()
    banner.append("🚀 ", style="bold")
    banner.append("Create Fullstack", style="bold blue")
    banner.append(" - Interactive Project Scaffolding\n\n", style="dim")
    banner.append("Generate a customized fullstack project with your preferred stack.", style="italic")

    console.print(Panel(banner, border_style="blue", padding=(1, 2)))
    console.print()


def _prompt_text(prompt: str, default: str) -> str:
    """Prompt for required text input with cancellation handling.

    Returns:
        User input string.

    """
    result = questionary.text(
        prompt,
        default=default,
        validate=lambda x: len(x) > 0 or "Value cannot be empty",
    ).ask()
    if result is None:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)
    return result


def _prompt_text_optional(prompt: str, default: str) -> str:
    """Prompt for optional text input with cancellation handling.

    Returns:
        User input string (may be empty).

    """
    result = questionary.text(prompt, default=default).ask()
    if result is None:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)
    return result


def _prompt_select(prompt: str, choices_list: list[dict[str, str]]) -> str:
    """Prompt for single selection with cancellation handling.

    Returns:
        Selected value.

    """
    result = questionary.select(
        prompt,
        choices=[questionary.Choice(c["name"], value=c["value"]) for c in choices_list],
    ).ask()
    if result is None:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)
    return result


def _prompt_checkbox(prompt: str, choices_list: list[dict[str, str]]) -> list[str]:
    """Prompt for multi-selection with cancellation handling.

    Returns:
        List of selected values.

    """
    result = questionary.checkbox(
        prompt,
        choices=[questionary.Choice(c["name"], value=c["value"]) for c in choices_list],
    ).ask()
    if result is None:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)
    return result


def _prompt_path(prompt: str, default: str) -> str:
    """Prompt for path input with cancellation handling.

    Returns:
        Selected path.

    """
    result = questionary.path(prompt, default=default, only_directories=True).ask()
    if result is None:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)
    return result


def _get_orm_choices(choices: dict[str, list[dict[str, str]]], database: str, backend: str) -> list[dict[str, str]]:
    """Get ORM choices based on database and backend selection.

    Returns:
        List of ORM choices appropriate for the selected database/backend.

    """
    if database == "mongodb":
        return [
            {"name": "Motor - Async MongoDB driver", "value": "motor"},
            {"name": "Beanie - Async ODM for MongoDB", "value": "beanie"},
            {"name": "None - Raw PyMongo", "value": "none"},
        ]
    if backend == "django":
        return [{"name": "Django ORM - Built-in Django ORM", "value": "django_orm"}]
    return choices["orm"]


def prompt_project_config() -> dict[str, Any]:
    """Prompt user for project configuration.

    Returns:
        Dictionary containing all project configuration options.

    """
    choices = get_choices()

    display_banner()

    # Gather all configuration through prompts
    project_name = _prompt_text("Project name:", "my-fullstack-app")
    description = _prompt_text_optional("Project description:", "A fullstack application")
    backend = _prompt_select("Backend framework:", choices["backend"])
    frontend = _prompt_select("Frontend framework:", choices["frontend"])
    database = _prompt_select("Database:", choices["database"])
    orm_choices = _get_orm_choices(choices, database, backend)
    orm = _prompt_select("ORM / Database driver:", orm_choices)
    auth = _prompt_select("Authentication:", choices["auth"])
    features = _prompt_checkbox("Additional features (space to select, enter to confirm):", choices["features"])
    output_dir = _prompt_path("Output directory:", f"./{project_name}")

    return {
        "project_name": project_name,
        "project_slug": project_name.lower().replace(" ", "-").replace("_", "-"),
        "description": description,
        "backend": backend,
        "frontend": frontend,
        "database": database,
        "orm": orm,
        "auth": auth,
        "features": features,
        "docker": "docker" in features,
        "cicd": "cicd" in features,
        "testing": "testing" in features,
        "linting": "linting" in features,
        "output_dir": output_dir,
    }


def display_summary(config: dict[str, Any]) -> None:
    """Display a summary of selected options."""
    console.print("\n")
    summary = Text()
    summary.append("📋 Project Configuration\n\n", style="bold")
    summary.append("  Project: ", style="dim")
    summary.append(f"{config['project_name']}\n", style="bold cyan")
    summary.append("  Backend: ", style="dim")
    summary.append(f"{config['backend'].title()}\n", style="green")
    summary.append("  Frontend: ", style="dim")
    summary.append(f"{config['frontend'].title()}\n", style="green")
    summary.append("  Database: ", style="dim")
    summary.append(f"{config['database'].title()}\n", style="green")
    summary.append("  ORM: ", style="dim")
    summary.append(f"{config['orm'].title()}\n", style="green")
    summary.append("  Auth: ", style="dim")
    summary.append(f"{config['auth'].title()}\n", style="green")

    if config["features"]:
        summary.append("  Features: ", style="dim")
        summary.append(f"{', '.join(config['features'])}\n", style="green")

    summary.append("\n  Output: ", style="dim")
    summary.append(f"{config['output_dir']}", style="yellow")

    console.print(Panel(summary, border_style="green", padding=(1, 2)))


def main() -> None:
    """Run the CLI application."""
    try:
        config = prompt_project_config()
        display_summary(config)

        # Confirm before generating
        confirm = questionary.confirm(
            "\nGenerate project with these settings?",
            default=True,
        ).ask()

        if not confirm:
            console.print("\n[yellow]Cancelled.[/yellow]")
            sys.exit(0)

        console.print("\n")

        # Generate the project
        with console.status("[bold green]Generating project...", spinner="dots"):
            generate_project(config)

        # Success message
        console.print("\n[bold green]✅ Project created successfully![/bold green]")
        console.print("\n[dim]Next steps:[/dim]")
        console.print(f"  cd {config['output_dir']}")

        if config["backend"] in {"fastapi", "flask", "litestar"}:
            console.print("  pip install -r backend/requirements.txt")
        elif config["backend"] == "django":
            console.print("  pip install -r requirements.txt")

        if config["frontend"] != "none":
            console.print("  cd frontend && npm install")

        if config["docker"]:
            console.print("  docker-compose up -d")

        console.print()

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
