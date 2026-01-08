# {{ project_name }} Backend

{{ description }}

## Development Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- Python 3.11 or higher

### Installation

```bash
# Install dependencies
cd backend
uv sync

# Activate virtual environment (optional, uv run handles this)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Running the Application

```bash
# Development mode with hot reload
uv run uvicorn app.main:app --reload

# Or activate venv first
source .venv/bin/activate
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Adding Dependencies

```bash
# Add a production dependency
uv add httpx

# Add a dev dependency
uv add --dev pytest-mock

# Update all dependencies
uv sync --upgrade
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_main.py
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy app
```

### Docker

```bash
# Build image
docker build -t {{ project_slug }}-backend .

# Run container
docker run -p 8000:8000 {{ project_slug }}-backend
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration settings
│   └── ...
├── tests/
│   └── ...
├── pyproject.toml       # Dependencies and tool configuration
├── .python-version      # Python version for uv
├── Dockerfile
└── README.md
```

## API Documentation

When the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

Create a `.env` file in the backend directory:

```env
APP_ENV=development
DEBUG=true
# Add other environment variables here
```
