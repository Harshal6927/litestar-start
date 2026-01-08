# Template System Implementation

## Overview

Implemented a comprehensive template system for litestar-start based on PRD-004. The system provides:

- **Template Loading**: Centralized template discovery and loading with prefix-based organization
- **Template Contexts**: Type-safe Pydantic models for template rendering
- **Template Inheritance**: Jinja2 template extends/blocks for code reuse
- **Custom Filters**: Snake/pascal/kebab case converters and other helpers
- **Validation**: Pre-render context validation
- **Caching**: Optional template caching for production use
- **Testing**: Comprehensive test suite

## Structure

```
src/litestar_start/
├── core/
│   ├── templates.py          # TemplateLoader and utilities
│   ├── context.py            # Pydantic context models
│   └── templates/
│       ├── base/             # Shared base templates
│       │   ├── gitignore.jinja
│       │   ├── readme.md.jinja
│       │   └── env.example.jinja
│       └── macros/           # Reusable Jinja macros
│           ├── python.jinja
│           └── javascript.jinja
├── backends/
│   ├── fastapi/
│   │   ├── generator.py      # Updated to use TemplateLoader
│   │   └── templates/        # FastAPI-specific templates
│   │       ├── app/
│   │       ├── api/
│   │       ├── pyproject.toml.jinja
│   │       └── gitignore.jinja
│   └── litestar/
│       ├── generator.py      # Updated to use TemplateLoader
│       └── templates/        # Litestar-specific templates
│           ├── app/
│           ├── controllers/
│           ├── pyproject.toml.jinja
│           └── gitignore.jinja
tests/
└── templates/
    ├── test_template_loader.py
    ├── test_context.py
    ├── test_fastapi_templates.py
    └── test_litestar_templates.py
```

## Key Features

### Template Loader

```python
from litestar_start.core.templates import TemplateLoader

loader = TemplateLoader()
# Register backend templates
loader.register_template_dir("fastapi", Path("backends/fastapi/templates"))

# Render with context
result = loader.render("fastapi:app/main.py.jinja", {
    "project_name": "My API",
    "description": "A cool API"
})
```

### Template Contexts

```python
from litestar_start.core.context import BackendContext

context = BackendContext(
    project_name="My API",
    project_slug="my-api",
    description="A cool API",
    backend="fastapi",
    dependencies=["fastapi>=0.109.0"]
)
```

### Custom Filters

- `snake_case`: Convert to snake_case
- `pascal_case`: Convert to PascalCase
- `kebab_case`: Convert to kebab-case
- `quote`: Wrap in quotes
- `indent`: Indent text by N spaces

### Template Inheritance

Base template:
```jinja
{% extends "base:gitignore.jinja" %}

{% block extra %}
# FastAPI specific
*.db
{% endblock %}
```

### Generators Updated

Both FastAPI and Litestar generators now use the template system:

- Removed hardcoded template strings
- Use `TemplateLoader` for all file generation
- Templates are co-located with generators
- Supports template extension and blocks for plugins

## Testing

Run tests:
```bash
source .venv/bin/activate
pytest tests/templates/ -v
```

All 33 tests pass ✓

## Migration Notes

- Old `_create_*_file()` methods removed from generators
- Templates moved from inline strings to `.jinja` files
- Generator `__init__` now registers templates with loader
- Context passed as dictionaries to `render()` method

## Next Steps

- Add templates for Docker/infrastructure
- Implement plugin template system
- Add template hot-reload in development
- Create template documentation generator
