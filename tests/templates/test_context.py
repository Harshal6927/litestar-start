"""Tests for template context models."""

import datetime

from litestar_start.core.context import BackendContext, DockerContext, FrontendContext, ProjectContext


class TestProjectContext:
    """Tests for ProjectContext model."""

    def test_project_context_creation(self):
        """Test creating a project context."""
        context = ProjectContext(
            project_name="Test Project",
            project_slug="test-project",
            description="A test project",
        )

        assert context.project_name == "Test Project"
        assert context.project_slug == "test-project"
        assert context.description == "A test project"
        assert context.author == ""
        assert context.year == datetime.datetime.now(tz=datetime.timezone.utc).year

    def test_project_context_with_author(self):
        """Test creating a project context with author."""
        context = ProjectContext(
            project_name="Test Project",
            project_slug="test-project",
            description="A test project",
            author="Test Author",
        )

        assert context.author == "Test Author"

    def test_project_context_allows_extra_fields(self):
        """Test that extra fields are allowed."""
        context = ProjectContext(
            project_name="Test Project",
            project_slug="test-project",
            description="A test project",
            custom_field="custom value",
        )

        # Extra fields should be accessible
        assert context.custom_field == "custom value"  # type: ignore[attr-defined]


class TestBackendContext:
    """Tests for BackendContext model."""

    def test_backend_context_creation(self):
        """Test creating a backend context."""
        context = BackendContext(
            project_name="Test Project",
            project_slug="test-project",
            description="A test project",
            backend="fastapi",
            database="postgresql",
            orm="sqlalchemy",
        )

        assert context.backend == "fastapi"
        assert context.database == "postgresql"
        assert context.orm == "sqlalchemy"
        assert context.python_version == "3.12"
        assert context.dependencies == []

    def test_backend_context_with_dependencies(self):
        """Test creating a backend context with dependencies."""
        deps = ["fastapi>=0.109.0", "sqlalchemy>=2.0.0"]
        context = BackendContext(
            project_name="Test Project",
            project_slug="test-project",
            description="A test project",
            backend="fastapi",
            dependencies=deps,
        )

        assert context.dependencies == deps


class TestFrontendContext:
    """Tests for FrontendContext model."""

    def test_frontend_context_creation(self):
        """Test creating a frontend context."""
        context = FrontendContext(
            project_name="Test Project",
            project_slug="test-project",
            description="A test project",
            frontend="react",
            typescript=True,
        )

        assert context.frontend == "react"
        assert context.typescript is True
        assert context.dependencies == {}


class TestDockerContext:
    """Tests for DockerContext model."""

    def test_docker_context_creation(self):
        """Test creating a docker context."""
        context = DockerContext(
            project_name="Test Project",
            project_slug="test-project",
            description="A test project",
            backend="fastapi",
            frontend="react",
            database="postgresql",
        )

        assert context.backend == "fastapi"
        assert context.frontend == "react"
        assert context.database == "postgresql"
        assert context.python_version == "3.12"
        assert context.node_version == "20"
