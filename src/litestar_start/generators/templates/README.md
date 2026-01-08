# {{ project_name }}

{{ description }}

## Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- [Node.js](https://nodejs.org/) v20+ (if using frontend)
- [Docker](https://www.docker.com/) & Docker Compose (optional)

### Development Setup

1. **Backend Setup**

   ```bash
   cd backend
   uv sync
   uv run uvicorn app.main:app --reload
   ```

   Backend will be available at `http://localhost:8000`

2. **Frontend Setup** (if applicable)

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- Backend: `http://localhost:8000`
{% if frontend != 'none' %}- Frontend: `http://localhost:3000`{% endif %}
{% if database == 'postgresql' %}- PostgreSQL: `localhost:5432`{% endif %}
{% if database == 'mongodb' %}- MongoDB: `localhost:27017`{% endif %}
{% if database == 'mysql' %}- MySQL: `localhost:3306`{% endif %}

## Project Structure

```
{{ project_slug }}/
├── backend/              # {{ backend }} backend
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   ├── .python-version
│   └── Dockerfile
{% if frontend != 'none' %}├── frontend/             # {{ frontend }} frontend
│   ├── src/
│   ├── package.json
│   └── Dockerfile{% endif %}
├── docker-compose.yml
└── README.md
```

## Documentation

- [Backend README](./backend/README.md)
{% if frontend != 'none' %}- [Frontend README](./frontend/README.md){% endif %}

## API Documentation

When the backend is running:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

{{ license }}
