"""Abstract base classes for generators and plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import msgspec

if TYPE_CHECKING:
    from pathlib import Path


class GeneratorContext(msgspec.Struct):
    """Context passed to all generators."""

    project_name: str
    project_slug: str
    description: str
    output_dir: Path
    config: dict[str, Any]


class BaseGenerator(ABC):
    """Abstract base for all generators."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this generator."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name for CLI display."""
        ...

    @abstractmethod
    def generate(self, context: GeneratorContext) -> None:
        """Generate files for this component.

        Args:
            context: Generator context with project configuration.

        """
        ...

    @abstractmethod
    def get_dependencies(self) -> list[str]:
        """Return list of package dependencies.

        Returns:
            List of package names with version specifiers.

        """
        ...


class PluginInterface(ABC):
    """Interface for framework plugins (ORMs, auth, etc.)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin identifier."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name for CLI display."""
        ...

    @property
    @abstractmethod
    def category(self) -> str:
        """Plugin category: 'orm', 'auth', 'cache', etc."""
        ...

    @abstractmethod
    def apply(self, context: GeneratorContext, base_files: dict[str, str]) -> dict[str, str]:
        """Modify or add files.

        Args:
            context: Generator context with project configuration.
            base_files: Dictionary mapping file paths to content.

        Returns:
            Updated file mapping with plugin modifications.

        """
        ...

    @abstractmethod
    def get_dependencies(self) -> list[str]:
        """Additional dependencies this plugin requires.

        Returns:
            List of package names with version specifiers.

        """
        ...

    @staticmethod
    def get_env_vars() -> dict[str, str]:
        """Environment variables to add to .env.example.

        Returns:
            Dictionary mapping variable names to default values.

        """
        return {}
