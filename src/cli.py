"""Command-line interface for litestar-start."""

import sys
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.generator import ProjectGenerator
from src.models import Database, Framework, Plugin, ProjectConfig
from src.utils import validate_project_name

console = Console()


def print_banner() -> None:
    """Print the welcome banner."""
    banner = Text("⚡ Litestar Start ⚡", style="bold cyan", justify="center")
    console.print(Panel(banner))
    console.print()


def ask_project_name() -> str:
    """Ask for the project name.

    Returns:
        The validated project name.

    """
    while True:
        name = questionary.text(
            "What is your project name?",
            default="my-litestar-app",
        ).ask()

        if name is None:  # User pressed Ctrl+C
            console.print("\n[yellow]Cancelled.[/yellow]")
            sys.exit(0)

        error = validate_project_name(name)
        if error:
            console.print(f"[red]{error}[/red]")
            continue

        return name


def ask_framework() -> Framework:
    """Ask for the backend framework.

    Returns:
        The selected framework.

    """
    choices = [
        questionary.Choice(title="Litestar", value=Framework.LITESTAR),
    ]

    result = questionary.select(
        "Select backend framework:",
        choices=choices,
    ).ask()

    if result is None:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)

    return result


def ask_database() -> Database:
    """Ask for the database choice.

    Returns:
        The selected database.

    """
    choices = [
        questionary.Choice(title="PostgreSQL", value=Database.POSTGRESQL),
        questionary.Choice(title="SQLite", value=Database.SQLITE),
        questionary.Choice(title="MySQL", value=Database.MYSQL),
        questionary.Choice(title="None (no database)", value=Database.NONE),
    ]

    result = questionary.select(
        "Select database:",
        choices=choices,
    ).ask()

    if result is None:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)

    return result


def ask_plugins(database: Database) -> list[Plugin]:
    """Ask for plugins to install.

    Args:
        database: The selected database to determine plugin availability.

    Returns:
        A list of selected plugins.

    """
    choices = []

    # SQLAlchemy only makes sense with a database
    if database != Database.NONE:
        choices.append(questionary.Choice(title="SQLAlchemy (ORM)", value=Plugin.SQLALCHEMY))

    choices.append(questionary.Choice(title="JWT (Authentication)", value=Plugin.JWT))

    if not choices:
        return []

    # Add "None" option
    choices.append(questionary.Choice(title="None (skip plugins)", value=None))

    result = questionary.checkbox(
        "Select plugins (space to select, enter to confirm):",
        choices=choices,
    ).ask()

    if result is None:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)

    # Filter out None values
    return [p for p in result if p is not None]


def ask_docker() -> tuple[bool, bool]:
    """Ask for Docker configuration.

    Returns:
        A tuple of (generate_dockerfile, generate_docker_infra).

    """
    docker = questionary.confirm(
        "Generate Dockerfile for the application?",
        default=False,
    ).ask()

    if docker is None:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)

    docker_infra = questionary.confirm(
        "Generate docker-compose.infra.yml for local development (database, etc.)?",
        default=True,
    ).ask()

    if docker_infra is None:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)

    return docker, docker_infra


def main() -> None:
    """Run the main CLI interface."""
    print_banner()

    try:
        # Gather project configuration
        name = ask_project_name()
        framework = ask_framework()
        database = ask_database()
        plugins = ask_plugins(database)
        docker, docker_infra = ask_docker()

        # Create project config
        config = ProjectConfig(
            name=name,
            framework=framework,
            database=database,
            plugins=plugins,
            docker=docker,
            docker_infra=docker_infra,
        )

        # Show summary
        console.print()
        console.print(
            Panel.fit(
                f"[bold]Project:[/bold] {config.name}\n"
                f"[bold]Framework:[/bold] {config.framework.value}\n"
                f"[bold]Database:[/bold] {config.database.value}\n"
                f"[bold]Plugins:[/bold] {', '.join(p.value for p in config.plugins) or 'None'}\n"
                f"[bold]Docker:[/bold] {'Yes' if config.docker else 'No'}\n"
                f"[bold]Docker Infra:[/bold] {'Yes' if config.docker_infra else 'No'}",
                title="Configuration Summary",
            ),
        )
        console.print()

        # Confirm
        proceed = questionary.confirm("Generate project?", default=True).ask()
        if not proceed:
            console.print("[yellow]Cancelled.[/yellow]")
            sys.exit(0)

        # Generate project
        output_dir = Path.cwd() / config.slug
        generator = ProjectGenerator(config, output_dir)

        with console.status("[bold green]Generating project..."):
            generator.generate()

        console.print()
        console.print(f"[bold green]✓[/bold green] Project created at [cyan]{output_dir}[/cyan]")
        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print(f"  cd {config.slug}")
        console.print("  uv sync")
        if config.needs_docker_infra:
            console.print("  docker compose -f docker-compose.infra.yml up -d")
        console.print("  litestar run --reload")
        console.print()

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
