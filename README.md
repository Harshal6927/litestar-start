# Litestar Start

An interactive CLI tool to scaffold fullstack projects with modular choices for backend, frontend, database, and authentication.

## Installation

```bash
pipx run litestar-start

# uv
uvx litestar-start
```

## Usage

```bash
litestar-start
```

This will launch an interactive prompt where you can select:

- **Project name**: Your project's name
- **Backend framework**: Litestar, FastAPI, Django or Flask
- **Frontend framework**: React, Vue, Svelte, or None
- **Database**: PostgreSQL, MySQL, SQLite, or MongoDB
- **ORM**: SQLAlchemy, Prisma, Django ORM, or None
- **Authentication**: JWT, Session, OAuth2, or None

## Generated Project Structure

Based on your selections, the tool generates a complete project structure:

```
my-project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   └── auth/
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── .gitignore
├── .env.example
└── README.md
```

## License

MIT
