"""Litestar project generator."""

from pathlib import Path

from jinja2 import Environment
from src.models import DatabaseConfig, ProjectConfig
from src.utils import get_package_dir, get_template_env, write_file


class LitestarGenerator:
    """Generates a Litestar project."""

    def __init__(self, config: ProjectConfig, output_dir: Path) -> None:
        """Initialize the generator.

        Args:
            config: Project configuration.
            output_dir: Directory where the project will be generated.

        """
        self.config = config
        self.output_dir = output_dir
        self.litestar_dir = get_package_dir() / "Litestar"

    def _get_template_context(self) -> dict:
        """Build the template context."""
        db_config = DatabaseConfig.for_database(self.config.database)

        return {
            "project": self.config,
            "project_name": self.config.name,
            "project_slug": self.config.slug,
            "database": self.config.database,
            "db_config": db_config,
            "has_sqlalchemy": self.config.has_sqlalchemy,
            "has_jwt": self.config.has_jwt,
            "has_database": self.config.database.value != "None",
            "docker": self.config.docker,
            "docker_infra": self.config.docker_infra,
        }

    def _render_templates(
        self,
        template_dir: Path,
        output_subdir: Path,
        env: Environment,
        context: dict,
        root_template_dir: Path | None = None,
    ) -> None:
        """Recursively render templates from a directory."""
        if root_template_dir is None:
            root_template_dir = template_dir

        for item in template_dir.iterdir():
            if item.is_dir():
                # Recurse into subdirectories
                self._render_templates(item, output_subdir / item.name, env, context, root_template_dir)
            elif item.suffix == ".jinja":
                # Render template - use path relative to the environment's loader root
                relative_to_loader = item.relative_to(root_template_dir)
                template_name = str(relative_to_loader).replace("\\", "/")

                # Remove .jinja extension for output
                output_name = item.stem
                output_path = output_subdir / output_name

                template = env.get_template(template_name)
                content = template.render(**context)
                write_file(output_path, content)

    def generate(self) -> None:
        """Generate the Litestar project."""
        context = self._get_template_context()

        # Generate base config files
        self._generate_config(context)

        # Generate base application
        self._generate_base(context)

        # Generate plugins
        self._generate_plugins(context)

        # Generate Docker files if requested
        if self.config.docker or self.config.needs_docker_infra:
            self._generate_containers(context)

    def _generate_config(self, context: dict) -> None:
        """Generate configuration files (pyproject.toml, .gitignore, etc.)."""
        config_dir = self.litestar_dir / "Config"
        env = get_template_env(config_dir)

        for template_file in config_dir.glob("*.jinja"):
            template_name = template_file.name
            output_name = template_file.stem  # Remove .jinja extension

            template = env.get_template(template_name)
            content = template.render(**context)
            write_file(self.output_dir / output_name, content)

    def _generate_base(self, context: dict) -> None:
        """Generate base application files."""
        base_dir = self.litestar_dir / "Base"
        env = get_template_env(base_dir)

        self._render_templates(base_dir, self.output_dir, env, context)

    def _generate_plugins(self, context: dict) -> None:
        """Generate plugin-specific files."""
        plugins_dir = self.litestar_dir / "Plugins"

        for plugin in self.config.plugins:
            plugin_dir = plugins_dir / plugin.value
            templates_dir = plugin_dir / "Templates"

            if templates_dir.exists():
                env = get_template_env(templates_dir)
                self._render_templates(templates_dir, self.output_dir, env, context)

    def _generate_containers(self, context: dict) -> None:
        """Generate Docker-related files."""
        containers_dir = self.litestar_dir / "Containers"
        env = get_template_env(containers_dir)

        # Generate Dockerfile if requested
        if self.config.docker:
            template = env.get_template("Dockerfile.jinja")
            content = template.render(**context)
            write_file(self.output_dir / "Dockerfile", content)

            # Also generate docker-compose.yml for the app
            template = env.get_template("docker-compose.yml.jinja")
            content = template.render(**context)
            write_file(self.output_dir / "docker-compose.yml", content)

        # Generate docker-compose.infra.yml if needed
        if self.config.needs_docker_infra:
            template = env.get_template("docker-compose.infra.yml.jinja")
            content = template.render(**context)
            write_file(self.output_dir / "docker-compose.infra.yml", content)
