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

        # Generate frontend if selected
        if self.config.has_frontend:
            self._generate_frontend(context)

        # Generate root files
        self._generate_root_files()

        # Generate infrastructure
        if self.config.has_docker:
            self._generate_docker(context)

        if self.config.has_cicd:
            self._generate_cicd(context)

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
        """Generate backend code.

        Args:
            context: Generator context.

        """
        backend_gen_class = GeneratorRegistry.get_backend(self.config.backend)
        if backend_gen_class:
            backend_gen = backend_gen_class()
            backend_gen.generate(context)
        else:
            console.print(f"[yellow]Warning: No generator found for backend '{self.config.backend}'[/yellow]")
            self._generate_fallback_backend(context)

    def _generate_frontend(self, context: GeneratorContext) -> None:
        """Generate frontend code.

        Args:
            context: Generator context.

        """
        frontend_gen_class = GeneratorRegistry.get_frontend(self.config.frontend)
        if frontend_gen_class:
            frontend_gen = frontend_gen_class()
            frontend_gen.generate(context)
        else:
            console.print(f"[yellow]Warning: No generator found for frontend '{self.config.frontend}'[/yellow]")

    def _generate_root_files(self) -> None:
        """Generate root project files."""
        self._generate_gitignore()
        self._generate_env_example()
        self._generate_readme()

    def _generate_gitignore(self) -> None:
        """Generate .gitignore file."""
        gitignore_content = (
            "# Python\n"
            "__pycache__/\n"
            "*.py[cod]\n"
            "*$py.class\n"
            "*.so\n"
            ".Python\n"
            "venv/\n"
            ".venv/\n"
            "ENV/\n"
            ".env\n"
            "uv.lock\n\n"
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
        frontend_text = self.config.frontend.title() if self.config.has_frontend else "None (API only)"
        auth_text = self.config.auth.title() if self.config.has_auth else "None"

        readme_lines = [
            f"# {self.config.project_name}",
            "",
            self.config.description,
            "",
            "## Tech Stack",
            "",
            f"- **Backend**: {self.config.backend.title()}",
            f"- **Frontend**: {frontend_text}",
            f"- **Database**: {self.config.database.title()}",
            f"- **ORM**: {self.config.orm.title()}",
            f"- **Auth**: {auth_text}",
            "",
            "## Getting Started",
            "",
            "### Backend",
            "",
            "```bash",
            "cd backend",
            "uv venv",
            "source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate",
            "uv pip install -e .",
        ]

        run_commands = {
            "fastapi": "uvicorn app.main:app --reload",
            "litestar": "litestar run --reload",
            "flask": "python app/main.py",
            "django": "python manage.py runserver",
        }
        readme_lines.extend([run_commands.get(self.config.backend, "python app/main.py"), "```"])

        if self.config.has_frontend:
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

        readme_lines.extend(["", "## License", "", "MIT"])

        write_file(self.output_dir / "README.md", "\n".join(readme_lines) + "\n")

    def _generate_docker(self, _context: GeneratorContext) -> None:
        """Generate Docker files."""
        # Docker generation will be handled by infrastructure module later

    def _generate_cicd(self, _context: GeneratorContext) -> None:
        """Generate CI/CD files."""
        # CI/CD generation will be handled by infrastructure module later

    def _generate_fallback_backend(self, _context: GeneratorContext) -> None:
        """Generate minimal backend structure when no generator is available."""
        backend_dir = self.output_dir / "backend"
        ensure_dir(backend_dir)

        app_dir = backend_dir / "app"
        ensure_dir(app_dir)

        write_file(app_dir / "__init__.py", '"""Backend application."""\n')
        write_file(
            app_dir / "main.py",
            f'"""Main application entry point."""\n\nprint("Welcome to {self.config.project_name}!")\n',
        )
