"""Configuration models for project generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import msgspec


class ProjectConfig(msgspec.Struct):
    """Project configuration model."""

    project_name: str
    project_slug: str
    description: str
    backend: str
    frontend: str
    database: str
    orm: str
    auth: str
    features: list[str] = []
    output_dir: Path = Path()

    @property
    def has_docker(self) -> bool:
        """Check if Docker is enabled."""
        return "docker" in self.features

    @property
    def has_cicd(self) -> bool:
        """Check if CI/CD is enabled."""
        return "cicd" in self.features

    @property
    def has_testing(self) -> bool:
        """Check if testing is enabled."""
        return "testing" in self.features

    @property
    def has_linting(self) -> bool:
        """Check if linting is enabled."""
        return "linting" in self.features

    @property
    def has_frontend(self) -> bool:
        """Check if frontend is enabled."""
        return self.frontend != "none"

    @property
    def has_auth(self) -> bool:
        """Check if authentication is enabled."""
        return self.auth != "none"

    def to_context(self) -> dict[str, Any]:
        """Convert to template context dictionary.

        Returns:
            Dictionary suitable for template rendering.

        """
        return {
            "project_name": self.project_name,
            "project_slug": self.project_slug,
            "description": self.description,
            "backend": self.backend,
            "frontend": self.frontend,
            "database": self.database,
            "orm": self.orm,
            "auth": self.auth,
            "features": self.features,
            "docker": self.has_docker,
            "cicd": self.has_cicd,
            "testing": self.has_testing,
            "linting": self.has_linting,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectConfig:
        """Create ProjectConfig from dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            ProjectConfig instance.

        """
        output_dir = data.get("output_dir", ".")
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)

        return cls(
            project_name=data["project_name"],
            project_slug=data.get("project_slug", data["project_name"].lower().replace(" ", "-")),
            description=data.get("description", ""),
            backend=data["backend"],
            frontend=data.get("frontend", "none"),
            database=data.get("database", "sqlite"),
            orm=data.get("orm", "none"),
            auth=data.get("auth", "none"),
            features=data.get("features", []),
            output_dir=output_dir,
        )
