"""Project generator orchestrator."""

from pathlib import Path

from litestar_start.models import Framework, ProjectConfig


class ProjectGenerator:
    """Orchestrates project generation based on configuration."""

    def __init__(self, config: ProjectConfig, output_dir: Path) -> None:
        """Initialize the generator.

        Args:
            config: Project configuration.
            output_dir: Directory where the project will be generated.

        """
        self.config = config
        self.output_dir = output_dir

    def generate(self) -> None:
        """Generate the project based on configuration."""
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Delegate to framework-specific generator
        if self.config.framework == Framework.LITESTAR:
            from litestar_start.Litestar.generator import LitestarGenerator

            generator = LitestarGenerator(self.config, self.output_dir)
            generator.generate()
        else:
            msg = f"Framework {self.config.framework} is not yet supported"
            raise NotImplementedError(msg)
