"""Tests for FastAPI templates."""

from pathlib import Path

import pytest

from litestar_start.core.templates import TemplateLoader


@pytest.fixture
def fastapi_loader():
    """Create a template loader with FastAPI templates registered."""
    loader = TemplateLoader()
    templates_path = (
        Path(__file__).parent.parent.parent / "src" / "litestar_start" / "backends" / "fastapi" / "templates"
    )
    loader.register_template_dir("fastapi", templates_path)
    return loader


class TestFastAPITemplates:
    """Tests for FastAPI template rendering."""

    def test_render_main_py(self, fastapi_loader, base_context):
        """Test rendering FastAPI main.py template."""
        result = fastapi_loader.render("fastapi:app/main.py.jinja", base_context)

        assert "from fastapi import FastAPI" in result
        assert 'title="Test Project"' in result
        assert 'description="A test project"' in result
        assert "async def root" in result
        assert "async def health" in result

    def test_render_config_py(self, fastapi_loader, base_context):
        """Test rendering FastAPI config.py template."""
        result = fastapi_loader.render("fastapi:app/config.py.jinja", base_context)

        assert "from pydantic_settings import BaseSettings" in result
        assert 'APP_NAME: str = "test-project"' in result
        assert "class Settings(BaseSettings)" in result

    def test_render_pyproject_toml(self, fastapi_loader, backend_context):
        """Test rendering FastAPI pyproject.toml template."""
        result = fastapi_loader.render("fastapi:pyproject.toml.jinja", backend_context)

        assert 'name = "test-project"' in result
        assert 'description = "A test project"' in result
        assert "fastapi>=0.109.0" in result
        assert "uvicorn>=0.27.0" in result

    def test_render_routes_py(self, fastapi_loader):
        """Test rendering FastAPI routes.py template."""
        result = fastapi_loader.render("fastapi:api/routes.py.jinja", {})

        assert "from fastapi import APIRouter" in result
        assert "router = APIRouter" in result
        assert "async def get_status" in result

    def test_render_gitignore(self, fastapi_loader):
        """Test rendering FastAPI gitignore template."""
        result = fastapi_loader.render("fastapi:gitignore.jinja", {})

        # Should contain base content
        assert "# Python" in result
        assert "__pycache__/" in result

        # Should contain FastAPI-specific content
        assert "# FastAPI specific" in result
        assert "*.db" in result
        assert ".pytest_cache/" in result
