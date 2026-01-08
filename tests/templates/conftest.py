"""Test fixtures for template tests."""

import pytest

from litestar_start.core.templates import TemplateLoader


@pytest.fixture
def template_loader():
    """Create a template loader instance."""
    return TemplateLoader()


@pytest.fixture
def base_context():
    """Base template context for testing."""
    return {
        "project_name": "Test Project",
        "project_slug": "test-project",
        "description": "A test project",
    }


@pytest.fixture
def backend_context(base_context):
    """Backend template context for testing."""
    return {
        **base_context,
        "dependencies": ["fastapi>=0.109.0", "uvicorn>=0.27.0"],
    }
