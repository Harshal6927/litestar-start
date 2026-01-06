"""Project generator that renders templates based on user configuration."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateError, select_autoescape
from rich.console import Console

console = Console()

_SPLIT_DEPTH = 2


def get_template_dir() -> Path:
    """Get the path to the templates directory.

    Returns:
        Path to the templates directory.

    """
    package_dir = Path(__file__).parent.parent.parent
    template_dir = package_dir / "templates"

    if not template_dir.exists():
        template_dir = Path(__file__).parent.parent.parent / "templates"

    return template_dir


def create_jinja_env(template_dir: Path) -> Environment:
    """Create a Jinja2 environment for template rendering.

    Returns:
        Configured Jinja2 Environment.

    """
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template(env: Environment, template_path: str, context: dict[str, Any]) -> str:
    """Render a single template with the given context.

    Returns:
        Rendered template content.

    """
    template = env.get_template(template_path)
    return template.render(**context)


def _check_module_inclusion(file_path: str, module: str, config_key: str, config: dict[str, Any]) -> bool | None:
    """Check if a module-specific file should be included.

    Returns:
        True if should include, False if should exclude, None if not applicable.

    """
    if f"{module}/" not in file_path:
        return None

    value = config.get(config_key, "")
    if value == "none":
        return False
    return f"{module}/{value}/" in file_path


def should_include_file(file_path: str, config: dict[str, Any]) -> bool:
    """Determine if a file should be included based on configuration.

    Returns:
        True if the file should be included, False otherwise.

    """
    # Check module-specific files
    modules = [
        ("backends", "backend"),
        ("frontends", "frontend"),
        ("auth", "auth"),
    ]

    for module, config_key in modules:
        result = _check_module_inclusion(file_path, module, config_key, config)
        if result is not None and not result:
            return False

    # Check feature flags
    feature_checks = [
        ("docker/", "docker"),
        ("cicd/", "cicd"),
        ("testing/", "testing"),
    ]

    return not any(pattern in file_path and not config.get(feature_key) for pattern, feature_key in feature_checks)


def _transform_path(path: str, output_prefix: str) -> str:
    """Transform a path by replacing prefix with output prefix.

    Returns:
        Transformed path.

    """
    parts = path.split("/", _SPLIT_DEPTH)
    suffix = parts[_SPLIT_DEPTH] if len(parts) > _SPLIT_DEPTH else parts[1]
    return f"{output_prefix}/{suffix}"


def get_output_path(template_path: str) -> str:
    """Convert template path to output path.

    Returns:
        Output path for the template.

    """
    path = template_path

    path_transforms = {
        "backends/": "backend",
        "frontends/": "frontend",
        "auth/": "backend/app/auth",
    }

    for prefix, output_prefix in path_transforms.items():
        if path.startswith(prefix):
            path = _transform_path(path, output_prefix)
            break
    else:
        # Handle other prefixes
        if path.startswith("docker/"):
            parts = path.split("/", 1)
            path = parts[1] if len(parts) > 1 else parts[0]
        elif path.startswith("cicd/"):
            parts = path.split("/", 1)
            path = f".github/workflows/{parts[1]}" if len(parts) > 1 else ".github/workflows"
        elif path.startswith("base/"):
            parts = path.split("/", 1)
            path = parts[1] if len(parts) > 1 else parts[0]

    return path.removesuffix(".jinja")


def copy_static_files(template_dir: Path, output_dir: Path, config: dict[str, Any]) -> None:
    """Copy static (non-template) files."""
    for root, dirs, files in template_dir.walk():
        dirs[:] = [d for d in dirs if not d.startswith(("__", "."))]

        for file in files:
            if file.endswith(".jinja") or file.startswith("."):
                continue

            src_path = root / file
            rel_path = src_path.relative_to(template_dir)

            if not should_include_file(str(rel_path), config):
                continue

            output_path = get_output_path(str(rel_path))
            dest_path = output_dir / output_path

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)


def render_templates(template_dir: Path, output_dir: Path, config: dict[str, Any]) -> None:
    """Render all Jinja templates."""
    env = create_jinja_env(template_dir)

    for root, dirs, files in template_dir.walk():
        dirs[:] = [d for d in dirs if not d.startswith(("__", "."))]

        for file in files:
            if not file.endswith(".jinja"):
                continue

            src_path = root / file
            rel_path = src_path.relative_to(template_dir)

            if not should_include_file(str(rel_path), config):
                continue

            output_path = get_output_path(str(rel_path))
            dest_path = output_dir / output_path

            try:
                content = render_template(env, str(rel_path), config)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_path.write_text(content, encoding="utf-8")
            except TemplateError as e:
                console.print(f"[yellow]Warning: Could not render {rel_path}: {e}[/yellow]")


def generate_project(config: dict[str, Any]) -> None:
    """Generate the project based on configuration."""
    template_dir = get_template_dir()
    output_dir = Path(config["output_dir"]).resolve()

    output_dir.mkdir(parents=True, exist_ok=True)

    if not template_dir.exists():
        console.print("[dim]Creating project structure...[/dim]")
        create_minimal_structure(output_dir, config)
        return

    render_templates(template_dir, output_dir, config)
    copy_static_files(template_dir, output_dir, config)

    console.print(f"[dim]Generated project at {output_dir}[/dim]")


def create_minimal_structure(output_dir: Path, config: dict[str, Any]) -> None:
    """Create minimal project structure when templates aren't available."""
    backend_dir = output_dir / "backend"
    backend_dir.mkdir(parents=True, exist_ok=True)

    app_dir = backend_dir / "app"
    app_dir.mkdir(exist_ok=True)

    (app_dir / "__init__.py").write_text('"""Backend application."""\n')

    # Create main.py based on backend choice
    main_content = _get_backend_main(config)
    main_content = main_content.replace("{{ project_name }}", config["project_name"])
    main_content = main_content.replace("{{ project_slug }}", config["project_slug"])
    main_content = main_content.replace("{{ description }}", config["description"])

    (app_dir / "main.py").write_text(main_content)

    # Create requirements.txt
    requirements = _get_requirements(config)
    (backend_dir / "requirements.txt").write_text("\n".join(sorted(requirements)) + "\n")

    # Create frontend if selected
    if config["frontend"] != "none":
        _create_frontend(output_dir, config)

    # Create root files
    _create_root_files(output_dir, config)

    # Create docker files if selected
    if config.get("docker"):
        _create_docker_files(output_dir, config)

    # Create CI/CD files if selected
    if config.get("cicd"):
        _create_cicd_files(output_dir, config)


def _get_backend_main(config: dict[str, Any]) -> str:
    """Get the main.py content for the selected backend.

    Returns:
        Content for the main.py file.

    """
    templates = {
        "fastapi": '''"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="{{ project_name }}",
    description="{{ description }}",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to {{ project_name }}!"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
''',
        "litestar": '''"""Litestar application entry point."""

from litestar import Litestar, get
from litestar.config.cors import CORSConfig


@get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Welcome to {{ project_name }}!"}


@get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


app = Litestar(
    route_handlers=[root, health],
    cors_config=CORSConfig(allow_origins=["*"]),
)
''',
        "flask": '''"""Flask application entry point."""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def root():
    """Root endpoint."""
    return jsonify({"message": "Welcome to {{ project_name }}!"})


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(debug=True)
''',
        "django": '''"""
Django settings for {{ project_slug }} project.
"""

# This is a placeholder. Run `django-admin startproject {{ project_slug }}` for full setup.
''',
    }
    return templates.get(config["backend"], templates["django"])


def _get_backend_requirements(backend: str) -> list[str]:
    """Get requirements for the selected backend.

    Returns:
        List of requirements for the backend.

    """
    backend_deps = {
        "fastapi": ["fastapi>=0.109.0", "uvicorn[standard]>=0.27.0"],
        "litestar": ["litestar>=2.5.0", "uvicorn[standard]>=0.27.0"],
        "flask": ["flask>=3.0.0", "flask-cors>=4.0.0"],
        "django": ["django>=5.0.0", "djangorestframework>=3.14.0"],
    }
    return backend_deps.get(backend, [])


def _get_database_requirements(database: str, orm: str) -> list[str]:
    """Get requirements for the selected database and ORM.

    Returns:
        List of requirements for the database/ORM combination.

    """
    requirements: list[str] = []

    if database == "postgresql":
        if orm == "sqlalchemy":
            requirements.extend(["sqlalchemy>=2.0.0", "psycopg2-binary>=2.9.9", "alembic>=1.13.0"])
        elif orm == "tortoise":
            requirements.extend(["tortoise-orm>=0.20.0", "asyncpg>=0.29.0"])
    elif database == "sqlite" and orm == "sqlalchemy":
        requirements.extend(["sqlalchemy>=2.0.0", "aiosqlite>=0.19.0", "alembic>=1.13.0"])
    elif database == "mongodb":
        if orm == "beanie":
            requirements.extend(["beanie>=1.24.0", "motor>=3.3.0"])
        else:
            requirements.append("motor>=3.3.0")

    return requirements


def _get_auth_requirements(auth: str) -> list[str]:
    """Get requirements for the selected auth method.

    Returns:
        List of requirements for authentication.

    """
    auth_deps = {
        "jwt": ["python-jose[cryptography]>=3.3.0", "passlib[bcrypt]>=1.7.4"],
        "session": ["itsdangerous>=2.1.0"],
        "oauth2": ["authlib>=1.3.0"],
    }
    return auth_deps.get(auth, [])


def _get_requirements(config: dict[str, Any]) -> list[str]:
    """Get the requirements list based on configuration.

    Returns:
        Complete list of requirements.

    """
    requirements = ["python-dotenv>=1.0.0"]
    requirements.extend(_get_backend_requirements(config["backend"]))
    requirements.extend(_get_database_requirements(config["database"], config["orm"]))
    requirements.extend(_get_auth_requirements(config["auth"]))
    return requirements


def _create_frontend(output_dir: Path, config: dict[str, Any]) -> None:
    """Create frontend project structure."""
    frontend_dir = output_dir / "frontend"
    frontend_dir.mkdir(exist_ok=True)

    package_json = {
        "name": config["project_slug"] + "-frontend",
        "private": True,
        "version": "0.0.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview",
        },
    }

    frontend_configs = {
        "react": {
            "dependencies": {"react": "^18.2.0", "react-dom": "^18.2.0"},
            "devDependencies": {"@vitejs/plugin-react": "^4.2.1", "vite": "^5.0.0"},
        },
        "vue": {
            "dependencies": {"vue": "^3.4.0"},
            "devDependencies": {"@vitejs/plugin-vue": "^5.0.0", "vite": "^5.0.0"},
        },
        "svelte": {
            "dependencies": {},
            "devDependencies": {
                "@sveltejs/vite-plugin-svelte": "^3.0.0",
                "svelte": "^4.2.0",
                "vite": "^5.0.0",
            },
        },
    }

    if config["frontend"] in frontend_configs:
        package_json.update(frontend_configs[config["frontend"]])

    (frontend_dir / "package.json").write_text(json.dumps(package_json, indent=2) + "\n")

    src_dir = frontend_dir / "src"
    src_dir.mkdir(exist_ok=True)

    _create_frontend_files(src_dir, frontend_dir, config)


def _create_frontend_files(src_dir: Path, frontend_dir: Path, config: dict[str, Any]) -> None:
    """Create frontend source files."""
    project_name = config["project_name"]
    description = config["description"]

    if config["frontend"] == "react":
        _create_react_files(src_dir, project_name, description)
    elif config["frontend"] == "vue":
        _create_vue_files(src_dir, project_name, description)
    elif config["frontend"] == "svelte":
        _create_svelte_files(src_dir, project_name, description)

    # Create index.html
    root_id = "root" if config["frontend"] == "react" else "app"
    main_ext = "jsx" if config["frontend"] == "react" else "js"
    index_content = (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "  <head>\n"
        '    <meta charset="UTF-8" />\n'
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        f"    <title>{project_name}</title>\n"
        "  </head>\n"
        "  <body>\n"
        f'    <div id="{root_id}"></div>\n'
        f'    <script type="module" src="/src/main.{main_ext}"></script>\n'
        "  </body>\n"
        "</html>\n"
    )
    (frontend_dir / "index.html").write_text(index_content)


def _create_react_files(src_dir: Path, project_name: str, description: str) -> None:
    """Create React source files."""
    app_content = (
        "import { useState } from 'react'\n\n"
        "function App() {\n"
        "  const [count, setCount] = useState(0)\n\n"
        "  return (\n"
        "    <div>\n"
        f"      <h1>{project_name}</h1>\n"
        f"      <p>{description}</p>\n"
        "      <button onClick={() => setCount((c) => c + 1)}>\n"
        "        Count: {count}\n"
        "      </button>\n"
        "    </div>\n"
        "  )\n"
        "}\n\n"
        "export default App\n"
    )
    (src_dir / "App.jsx").write_text(app_content)

    main_content = (
        "import React from 'react'\n"
        "import ReactDOM from 'react-dom/client'\n"
        "import App from './App.jsx'\n\n"
        "ReactDOM.createRoot(document.getElementById('root')).render(\n"
        "  <React.StrictMode>\n"
        "    <App />\n"
        "  </React.StrictMode>,\n"
        ")\n"
    )
    (src_dir / "main.jsx").write_text(main_content)


def _create_vue_files(src_dir: Path, project_name: str, description: str) -> None:
    """Create Vue source files."""
    app_content = (
        "<script setup>\n"
        "import { ref } from 'vue'\n\n"
        "const count = ref(0)\n"
        "</script>\n\n"
        "<template>\n"
        "  <div>\n"
        f"    <h1>{project_name}</h1>\n"
        f"    <p>{description}</p>\n"
        '    <button @click="count++">Count: {{ count }}</button>\n'
        "  </div>\n"
        "</template>\n"
    )
    (src_dir / "App.vue").write_text(app_content)

    main_content = "import { createApp } from 'vue'\nimport App from './App.vue'\n\ncreateApp(App).mount('#app')\n"
    (src_dir / "main.js").write_text(main_content)


def _create_svelte_files(src_dir: Path, project_name: str, description: str) -> None:
    """Create Svelte source files."""
    app_content = (
        "<script>\n"
        "  let count = 0\n"
        "</script>\n\n"
        "<main>\n"
        f"  <h1>{project_name}</h1>\n"
        f"  <p>{description}</p>\n"
        "  <button on:click={() => count++}>\n"
        "    Count: {count}\n"
        "  </button>\n"
        "</main>\n"
    )
    (src_dir / "App.svelte").write_text(app_content)

    main_content = (
        "import App from './App.svelte'\n\n"
        "const app = new App({\n"
        "  target: document.getElementById('app'),\n"
        "})\n\n"
        "export default app\n"
    )
    (src_dir / "main.js").write_text(main_content)


def _create_root_files(output_dir: Path, config: dict[str, Any]) -> None:
    """Create root project files."""
    gitignore = (
        "# Python\n"
        "__pycache__/\n"
        "*.py[cod]\n"
        "*$py.class\n"
        "*.so\n"
        ".Python\n"
        "venv/\n"
        ".venv/\n"
        "ENV/\n"
        ".env\n\n"
        "# Node\n"
        "node_modules/\n"
        "dist/\n"
        ".cache/\n\n"
        "# IDE\n"
        ".idea/\n"
        ".vscode/\n"
        "*.swp\n"
        "*.swo\n\n"
        "# OS\n"
        ".DS_Store\n"
        "Thumbs.db\n\n"
        "# Project\n"
        "*.log\n"
        ".coverage\n"
        "htmlcov/\n"
    )
    (output_dir / ".gitignore").write_text(gitignore)

    _create_env_example(output_dir, config)
    _create_readme(output_dir, config)


def _create_env_example(output_dir: Path, config: dict[str, Any]) -> None:
    """Create .env.example file."""
    env_lines = [
        f"# {config['project_name']} Environment Variables",
        "",
        "# Application",
        f"APP_NAME={config['project_slug']}",
        "APP_ENV=development",
        "DEBUG=true",
        "",
        "# Database",
    ]

    db_urls = {
        "postgresql": f"DATABASE_URL=postgresql://user:password@localhost:5432/{config['project_slug']}",
        "mysql": f"DATABASE_URL=mysql://user:password@localhost:3306/{config['project_slug']}",
        "sqlite": "DATABASE_URL=sqlite:///./app.db",
        "mongodb": f"MONGODB_URL=mongodb://localhost:27017/{config['project_slug']}",
    }

    if config["database"] in db_urls:
        env_lines.append(db_urls[config["database"]])

    env_lines.extend(("", "# Authentication"))
    if config["auth"] != "none":
        env_lines.append("SECRET_KEY=your-secret-key-here")
    if config["auth"] == "jwt":
        env_lines.append("JWT_SECRET=your-jwt-secret-here")

    (output_dir / ".env.example").write_text("\n".join(env_lines) + "\n")


def _create_readme(output_dir: Path, config: dict[str, Any]) -> None:
    """Create README.md file."""
    frontend_text = config["frontend"].title() if config["frontend"] != "none" else "None (API only)"
    auth_text = config["auth"].title() if config["auth"] != "none" else "None"

    readme_lines = [
        f"# {config['project_name']}",
        "",
        config["description"],
        "",
        "## Tech Stack",
        "",
        f"- **Backend**: {config['backend'].title()}",
        f"- **Frontend**: {frontend_text}",
        f"- **Database**: {config['database'].title()}",
        f"- **ORM**: {config['orm'].title()}",
        f"- **Auth**: {auth_text}",
        "",
        "## Getting Started",
        "",
        "### Backend",
        "",
        "```bash",
        "cd backend",
        "python -m venv venv",
        "source venv/bin/activate  # On Windows: venv\\Scripts\\activate",
        "pip install -r requirements.txt",
    ]

    run_commands = {
        "fastapi": "uvicorn app.main:app --reload",
        "litestar": "uvicorn app.main:app --reload",
        "flask": "python app/main.py",
        "django": "python manage.py runserver",
    }
    readme_lines.extend(
        (
            run_commands.get(config["backend"], "python app/main.py"),
            "```",
        ),
    )

    if config["frontend"] != "none":
        readme_lines.extend(
            [
                "",
                "### Frontend",
                "",
                "```bash",
                "cd frontend",
                "npm install",
                "npm run dev",
                "```",
            ],
        )

    readme_lines.extend(
        [
            "",
            "## License",
            "",
            "MIT",
        ],
    )

    (output_dir / "README.md").write_text("\n".join(readme_lines) + "\n")


def _create_docker_files(output_dir: Path, config: dict[str, Any]) -> None:
    """Create Docker-related files."""
    backend_dir = output_dir / "backend"

    # Backend Dockerfile
    dockerfile_lines = [
        "FROM python:3.12-slim",
        "",
        "WORKDIR /app",
        "",
        "COPY requirements.txt .",
        "RUN pip install --no-cache-dir -r requirements.txt",
        "",
        "COPY . .",
        "",
    ]

    cmd_by_backend = {
        "fastapi": 'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]',
        "litestar": 'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]',
        "flask": 'CMD ["python", "app/main.py"]',
        "django": 'CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]',
    }
    dockerfile_lines.append(cmd_by_backend.get(config["backend"], 'CMD ["python", "app/main.py"]'))

    (backend_dir / "Dockerfile").write_text("\n".join(dockerfile_lines) + "\n")

    _create_docker_compose(output_dir, config)


def _create_docker_compose(output_dir: Path, config: dict[str, Any]) -> None:
    """Create docker-compose.yml file."""
    compose_lines = [
        "version: '3.8'",
        "",
        "services:",
        "  backend:",
        "    build:",
        "      context: ./backend",
        "      dockerfile: Dockerfile",
        "    ports:",
        '      - "8000:8000"',
        "    environment:",
        "      - APP_ENV=development",
    ]

    if config["database"] != "sqlite":
        compose_lines.extend(
            [
                "    depends_on:",
                "      - db",
            ],
        )

    compose_lines.extend(
        [
            "    volumes:",
            "      - ./backend:/app",
        ],
    )

    if config["frontend"] != "none":
        compose_lines.extend(
            [
                "",
                "  frontend:",
                "    build:",
                "      context: ./frontend",
                "      dockerfile: Dockerfile",
                "    ports:",
                '      - "3000:3000"',
                "    volumes:",
                "      - ./frontend:/app",
                "      - /app/node_modules",
            ],
        )

    if config["database"] == "postgresql":
        compose_lines.extend(
            [
                "",
                "  db:",
                "    image: postgres:16-alpine",
                "    environment:",
                "      POSTGRES_USER: postgres",
                "      POSTGRES_PASSWORD: postgres",
                f"      POSTGRES_DB: {config['project_slug']}",
                "    ports:",
                '      - "5432:5432"',
                "    volumes:",
                "      - postgres_data:/var/lib/postgresql/data",
            ],
        )
    elif config["database"] == "mongodb":
        compose_lines.extend(
            [
                "",
                "  db:",
                "    image: mongo:7",
                "    ports:",
                '      - "27017:27017"',
                "    volumes:",
                "      - mongo_data:/data/db",
            ],
        )

    if config["database"] in {"postgresql", "mongodb"}:
        compose_lines.extend(
            [
                "",
                "volumes:",
            ],
        )
        if config["database"] == "postgresql":
            compose_lines.append("  postgres_data:")
        elif config["database"] == "mongodb":
            compose_lines.append("  mongo_data:")

    (output_dir / "docker-compose.yml").write_text("\n".join(compose_lines) + "\n")


def _create_cicd_files(output_dir: Path, config: dict[str, Any]) -> None:
    """Create CI/CD workflow files."""
    workflows_dir = output_dir / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    ci_lines = [
        "name: CI",
        "",
        "on:",
        "  push:",
        "    branches: [main]",
        "  pull_request:",
        "    branches: [main]",
        "",
        "jobs:",
        "  backend:",
        "    runs-on: ubuntu-latest",
        "",
        "    steps:",
        "      - uses: actions/checkout@v4",
        "",
        "      - name: Set up Python",
        "        uses: actions/setup-python@v5",
        "        with:",
        "          python-version: '3.12'",
        "",
        "      - name: Install dependencies",
        "        run: |",
        "          cd backend",
        "          pip install -r requirements.txt",
    ]

    if config.get("testing"):
        ci_lines.append("          pip install pytest pytest-cov")
        ci_lines.extend(
            [
                "",
                "      - name: Run tests",
                "        run: |",
                "          cd backend",
                "          pytest --cov=app",
            ],
        )

    if config["frontend"] != "none":
        ci_lines.extend(
            [
                "",
                "  frontend:",
                "    runs-on: ubuntu-latest",
                "",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "",
                "      - name: Setup Node.js",
                "        uses: actions/setup-node@v4",
                "        with:",
                "          node-version: '20'",
                "",
                "      - name: Install dependencies",
                "        run: |",
                "          cd frontend",
                "          npm ci",
                "",
                "      - name: Build",
                "        run: |",
                "          cd frontend",
                "          npm run build",
            ],
        )

    (workflows_dir / "ci.yml").write_text("\n".join(ci_lines) + "\n")
