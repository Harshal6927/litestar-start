#!/usr/bin/env python3
"""Prepare a new release by bumping version numbers."""

import re
import sys
from enum import StrEnum
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt

console = Console()


class BumpType(StrEnum):
    """Enum for version bump types."""

    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"
    ALPHA = "alpha"
    BETA = "beta"


def get_current_version(pyproject_path: Path) -> str:
    """Extract current version from pyproject.toml.

    Returns:
        Current version string.

    """
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version = "(\d+\.\d+\.\d+(?:[ab]\d+)?)"', content)
    if not match:
        console.print("[red]Could not find version in pyproject.toml[/red]")
        sys.exit(1)
    return match.group(1)


def bump_version(current_version: str, bump_type: BumpType) -> str:
    """Calculate new version based on bump type.

    Returns:
        New version string.

    """
    # Parse version with optional alpha/beta suffix
    base_match = re.match(r"(\d+)\.(\d+)\.(\d+)(?:([ab])(\d+))?", current_version)
    if not base_match:
        console.print(f"[red]Invalid version format: {current_version}[/red]")
        sys.exit(1)

    major = int(base_match.group(1))
    minor = int(base_match.group(2))
    patch = int(base_match.group(3))
    pre_release_type = base_match.group(4)  # 'a' or 'b' or None
    pre_release_num = int(base_match.group(5)) if base_match.group(5) else 0

    if bump_type == BumpType.MAJOR:
        major += 1
        minor = 0
        patch = 0
        return f"{major}.{minor}.{patch}"
    if bump_type == BumpType.MINOR:
        minor += 1
        patch = 0
        return f"{major}.{minor}.{patch}"
    if bump_type == BumpType.PATCH:
        patch += 1
        return f"{major}.{minor}.{patch}"
    if bump_type == BumpType.ALPHA:
        if pre_release_type == "a":
            # Increment alpha number
            return f"{major}.{minor}.{patch}a{pre_release_num + 1}"
        # Start new alpha series
        return f"{major}.{minor}.{patch}a1"
    if bump_type == BumpType.BETA:
        if pre_release_type == "b":
            # Increment beta number
            return f"{major}.{minor}.{patch}b{pre_release_num + 1}"
        # Start new beta series
        return f"{major}.{minor}.{patch}b1"

    return f"{major}.{minor}.{patch}"


def update_file(path: Path, pattern: str, replacement: str) -> None:
    """Update file content using regex pattern."""
    content = path.read_text(encoding="utf-8")
    if not re.search(pattern, content):
        console.print(f"[yellow]Warning: Pattern not found in {path.name}[/yellow]")
        return
    new_content = re.sub(pattern, replacement, content)
    path.write_text(new_content, encoding="utf-8")


def main() -> None:
    """Execute the release preparation process."""
    root_dir = Path(__file__).parent.parent
    pyproject_path = root_dir / "pyproject.toml"

    if not pyproject_path.exists():
        console.print("[red]Could not find pyproject.toml.[/red]")
        sys.exit(1)

    current_version = get_current_version(pyproject_path)
    console.print(f"Current version: [bold cyan]{current_version}[/bold cyan]")

    bump_type = Prompt.ask(
        "Select bump type",
        choices=[t.value for t in BumpType],
        default=BumpType.PATCH.value,
    )

    new_version = bump_version(current_version, BumpType(bump_type))
    console.print(f"Bumping to: [bold green]{new_version}[/bold green]")

    # Update pyproject.toml
    update_file(
        pyproject_path,
        r'version = "\d+\.\d+\.\d+(?:[ab]\d+)?"',
        f'version = "{new_version}"',
    )
    console.print(f"[green]✓[/green] Updated {pyproject_path.name}")


if __name__ == "__main__":
    main()
