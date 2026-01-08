"""Tests for the template loading system."""

import pytest

from litestar_start.core.templates import (
    CachedTemplateLoader,
    TemplateValidator,
)


class TestTemplateLoader:
    """Tests for TemplateLoader class."""

    def test_template_loader_initialization(self, template_loader):
        """Test that template loader initializes correctly."""
        assert template_loader is not None
        assert template_loader.env is not None

    def test_custom_filters_available(self, template_loader):
        """Test that custom filters are registered."""
        assert "snake_case" in template_loader.env.filters
        assert "pascal_case" in template_loader.env.filters
        assert "kebab_case" in template_loader.env.filters
        assert "quote" in template_loader.env.filters
        assert "indent" in template_loader.env.filters

    def test_custom_globals_available(self, template_loader):
        """Test that custom globals are registered."""
        assert "now" in template_loader.env.globals
        assert "year" in template_loader.env.globals

    def test_snake_case_filter(self, template_loader):
        """Test snake_case filter."""
        filter_func = template_loader.env.filters["snake_case"]
        assert filter_func("Hello World") == "hello_world"
        assert filter_func("hello-world") == "hello_world"
        assert filter_func("HelloWorld") == "helloworld"

    def test_pascal_case_filter(self, template_loader):
        """Test pascal_case filter."""
        filter_func = template_loader.env.filters["pascal_case"]
        assert filter_func("hello_world") == "HelloWorld"
        assert filter_func("hello-world") == "HelloWorld"

    def test_kebab_case_filter(self, template_loader):
        """Test kebab_case filter."""
        filter_func = template_loader.env.filters["kebab_case"]
        assert filter_func("hello_world") == "hello-world"
        assert filter_func("Hello World") == "hello-world"

    def test_quote_filter(self, template_loader):
        """Test quote filter."""
        filter_func = template_loader.env.filters["quote"]
        assert filter_func("test") == '"test"'

    def test_render_base_gitignore(self, template_loader):
        """Test rendering base gitignore template."""
        result = template_loader.render("base:gitignore.jinja", {})
        assert "# Python" in result
        assert "__pycache__/" in result
        assert "node_modules/" in result

    def test_render_base_readme(self, template_loader, base_context):
        """Test rendering base readme template."""
        result = template_loader.render("base:readme.md.jinja", base_context)
        assert "Test Project" in result
        assert "A test project" in result

    def test_template_render_error(self, template_loader):
        """Test that invalid template raises error."""
        with pytest.raises(Exception):  # Jinja will raise TemplateNotFound
            template_loader.render("nonexistent:template.jinja", {})


class TestTemplateValidator:
    """Tests for TemplateValidator class."""

    def test_validation_passes_with_required_keys(self):
        """Test validation passes when all required keys are present."""
        context = {"project_name": "Test", "description": "Test project"}
        errors = TemplateValidator.validate("fastapi:app/main.py.jinja", context)
        assert len(errors) == 0

    def test_validation_fails_with_missing_keys(self):
        """Test validation fails when required keys are missing."""
        context = {"project_name": "Test"}
        errors = TemplateValidator.validate("fastapi:app/main.py.jinja", context)
        assert len(errors) > 0
        assert "description" in errors[0]

    def test_validation_empty_for_unknown_template(self):
        """Test validation returns no errors for unknown template."""
        context = {}
        errors = TemplateValidator.validate("unknown:template.jinja", context)
        assert len(errors) == 0


class TestCachedTemplateLoader:
    """Tests for CachedTemplateLoader class."""

    def test_cached_loader_initialization(self):
        """Test cached loader initializes correctly."""
        loader = CachedTemplateLoader(cache_size=64)
        assert loader is not None
        assert loader._cache_size == 64

    def test_template_caching(self):
        """Test that templates are cached."""
        loader = CachedTemplateLoader()
        context = {"project_name": "Test", "description": "Test"}

        # First render
        result1 = loader.render("base:readme.md.jinja", context)

        # Second render should use cache
        result2 = loader.render("base:readme.md.jinja", context)

        assert result1 == result2
        assert "Test" in result1

    def test_cache_clear(self):
        """Test clearing the cache."""
        loader = CachedTemplateLoader()
        context = {"project_name": "Test", "description": "Test"}

        # Render a template
        loader.render("base:readme.md.jinja", context)

        # Clear cache
        loader.clear_cache()

        # Cache should be empty
        assert len(loader._template_cache) == 0
