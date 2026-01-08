"""Template context models."""

from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectContext(BaseModel):
    """Base context available to all templates."""

    model_config = ConfigDict(extra="allow")

    project_name: str
    project_slug: str
    description: str
    author: str = ""
    year: int = Field(default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc).year)


class BackendContext(ProjectContext):
    """Context for backend templates."""

    backend: str
    database: str = ""
    orm: str = ""
    auth: str = ""
    python_version: str = "3.12"
    dependencies: list[str] = Field(default_factory=list)
    dev_dependencies: list[str] = Field(default_factory=list)
    env_vars: dict[str, str] = Field(default_factory=dict)


class FrontendContext(ProjectContext):
    """Context for frontend templates."""

    frontend: str
    typescript: bool = False
    dependencies: dict[str, str] = Field(default_factory=dict)
    dev_dependencies: dict[str, str] = Field(default_factory=dict)


class DockerContext(ProjectContext):
    """Context for Docker templates."""

    backend: str
    frontend: str
    database: str
    python_version: str = "3.12"
    node_version: str = "20"
