"""Main project orchestrator for generating complete projects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from litestar_start.core.base import GeneratorContext
from litestar_start.core.utils import ensure_dir, write_file
from litestar_start.generators.registry import GeneratorRegistry

if TYPE_CHECKING:
    from litestar_start.core.config import ProjectConfig

console = Console()


class ProjectOrchestrator:
    """Orchestrates the generation of a complete project."""

    def __init__(self, config: ProjectConfig) -> None:
        """Initialize the project orchestrator.

        Args:
            config: Project configuration.

        """
        self.config = config
        self.output_dir = config.output_dir.resolve()
        ensure_dir(self.output_dir)

    def generate(self) -> None:
        """Generate the complete project."""
        context = self._create_context()

        # Generate backend
        self._generate_backend(context)

        # Generate root files
        self._generate_root_files()

        # Generate docker-compose if docker enabled
        if self.config.has_docker:
            self._generate_docker_compose()

        console.print(f"[dim]Generated project at {self.output_dir}[/dim]")

    def _create_context(self) -> GeneratorContext:
        """Create generator context from config.

        Returns:
            GeneratorContext instance.

        """
        return GeneratorContext(
            project_name=self.config.project_name,
            project_slug=self.config.project_slug,
            description=self.config.description,
            output_dir=self.output_dir,
            config=self.config.to_context(),
        )

    def _generate_backend(self, context: GeneratorContext) -> None:
        """Generate backend code."""
        backend_gen_class = GeneratorRegistry.get_backend(self.config.backend)
        if backend_gen_class:
            backend_gen = backend_gen_class()
            backend_gen.generate(context)
        else:
            console.print(f"[red]Error: No generator found for backend '{self.config.backend}'[/red]")

    def _generate_root_files(self) -> None:
        """Generate root project files."""
        self._generate_gitignore()
        self._generate_env_example()
        self._generate_readme()

    def _generate_gitignore(self) -> None:
        """Generate .gitignore file."""
        gitignore_content = """\
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
ENV/
.env
uv.lock

# Node
node_modules/
dist/
.cache/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project
*.log
.coverage
htmlcov/
"""
        write_file(self.output_dir / ".gitignore", gitignore_content)

    def _generate_env_example(self) -> None:
        """Generate .env.example file."""
        env_lines = [
            f"# {self.config.project_name} Environment Variables",
            "",
            "# Application",
            f"APP_NAME={self.config.project_slug}",
            "APP_ENV=development",
            "DEBUG=true",
            "",
            "# Database",
        ]

        db_urls = {
            "postgresql": f"DATABASE_URL=postgresql://user:password@localhost:5432/{self.config.project_slug}",
            "mysql": f"DATABASE_URL=mysql://user:password@localhost:3306/{self.config.project_slug}",
            "sqlite": "DATABASE_URL=sqlite:///./app.db",
            "mongodb": f"MONGODB_URL=mongodb://localhost:27017/{self.config.project_slug}",
        }

        if self.config.database in db_urls:
            env_lines.append(db_urls[self.config.database])

        env_lines.extend(["", "# Authentication"])
        if self.config.has_auth:
            env_lines.append("SECRET_KEY=your-secret-key-here")
        if self.config.auth == "jwt":
            env_lines.append("JWT_SECRET=your-jwt-secret-here")

        write_file(self.output_dir / ".env.example", "\n".join(env_lines) + "\n")

    def _generate_readme(self) -> None:
        """Generate README.md file."""
        auth_text = self.config.auth.title() if self.config.has_auth else "None"

        readme_lines = [
            f"# {self.config.project_name}",
            "",
            self.config.description,
            "",
            "## Tech Stack",
            "",
            f"- **Framework**: {self.config.backend.title()}",
            f"- **Database**: {self.config.database.title()}",
            f"- **ORM**: {self.config.orm.title()}",
            f"- **Auth**: {auth_text}",
            "",
            "## Getting Started",
            "",
            "```bash",
            "uv sync",
            "uv run uvicorn app.main:app --reload",
            "```",
        ]

        readme_lines.extend(["", "## License", "", "MIT"])

        write_file(self.output_dir / "README.md", "\n".join(readme_lines) + "\n")

    def _generate_docker_compose(self) -> None:
        """Generate docker-compose.yml file."""
        compose_lines = [
            "services:",
            "  app:",
            "    build:",
            "      context: .",
            "      dockerfile: Dockerfile",
            "    ports:",
            '      - "8000:8000"',
            "    environment:",
            "      - APP_ENV=development",
            f"      - APP_NAME={self.config.project_slug}",
        ]

        if self.config.database not in {"sqlite", "none"}:
            compose_lines.extend(
                [
                    "    depends_on:",
                    "      - db",
                ],
            )

        compose_lines.extend(
            [
                "    volumes:",
                "      - .:/app",
            ],
        )

        if self.config.database == "postgresql":
            compose_lines.extend(
                [
                    "",
                    "  db:",
                    "    image: postgres:16-alpine",
                    "    environment:",
                    "      POSTGRES_USER: postgres",
                    "      POSTGRES_PASSWORD: postgres",
                    f"      POSTGRES_DB: {self.config.project_slug}",
                    "    ports:",
                    '      - "5432:5432"',
                    "    volumes:",
                    "      - postgres_data:/var/lib/postgresql/data",
                    "",
                    "volumes:",
                    "  postgres_data:",
                ],
            )
        elif self.config.database == "mongodb":
            compose_lines.extend(
                [
                    "",
                    "  db:",
                    "    image: mongo:7",
                    "    ports:",
                    '      - "27017:27017"',
                    "    volumes:",
                    "      - mongo_data:/data/db",
                    "",
                    "volumes:",
                    "  mongo_data:",
                ],
            )

        write_file(self.output_dir / "docker-compose.yml", "\n".join(compose_lines) + "\n")
