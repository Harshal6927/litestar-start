"""Tests for Litestar templates."""

from pathlib import Path

import pytest

from litestar_start.core.templates import TemplateLoader


@pytest.fixture
def litestar_loader():
    """Create a template loader with Litestar templates registered."""
    loader = TemplateLoader()
    templates_path = (
        Path(__file__).parent.parent.parent / "src" / "litestar_start" / "backends" / "litestar" / "templates"
    )
    loader.register_template_dir("litestar", templates_path)
    return loader


class TestLitestarTemplates:
    """Tests for Litestar template rendering."""

    def test_render_main_py(self, litestar_loader, base_context):
        """Test rendering Litestar main.py template."""
        result = litestar_loader.render("litestar:app/main.py.jinja", base_context)

        assert "from litestar import Litestar, get" in result
        assert "from litestar.config.cors import CORSConfig" in result
        assert "async def root" in result
        assert "async def health" in result
        assert "app = Litestar" in result

    def test_render_config_py(self, litestar_loader, base_context):
        """Test rendering Litestar config.py template."""
        result = litestar_loader.render("litestar:app/config.py.jinja", base_context)

        assert "import msgspec" in result
        assert 'APP_NAME: str = "test-project"' in result
        assert "class Settings" in result

    def test_render_pyproject_toml(self, litestar_loader, backend_context):
        """Test rendering Litestar pyproject.toml template."""
        result = litestar_loader.render("litestar:pyproject.toml.jinja", backend_context)

        assert 'name = "test-project"' in result
        assert 'description = "A test project"' in result
        assert "fastapi>=0.109.0" in result  # from backend_context dependencies

    def test_render_controller_py(self, litestar_loader):
        """Test rendering Litestar base controller template."""
        result = litestar_loader.render("litestar:controllers/base.py.jinja", {})

        assert "from litestar import Controller, get" in result
        assert "class BaseController(Controller)" in result
        assert "async def get_status" in result

    def test_render_gitignore(self, litestar_loader):
        """Test rendering Litestar gitignore template."""
        result = litestar_loader.render("litestar:gitignore.jinja", {})

        # Should contain base content
        assert "# Python" in result
        assert "__pycache__/" in result

        # Should contain Litestar-specific content
        assert "# Litestar specific" in result
        assert "*.db" in result
