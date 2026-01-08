# Developer Guide

Welcome to the `litestar-start` developer documentation! This guide will help you understand the project structure, set up your development environment, and contribute new features.

## Quick Start

### Prerequisites

*   **Python**: 3.10 or higher
*   **uv**: Universal Python Package Manager (Required for dependency management)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Harshal6927/litestar-start.git
    cd litestar-start
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Run the CLI locally:**
    ```bash
    uv run litestar-start
    ```

## Project Architecture

The project is built around a modular **Generator** pattern.

### Core Components (`src/litestar_start/core/`)
*   **`Context`**: Holds the global state of the generation process (user selections, paths).
*   **`Config`**: Pydantic models defining the project configuration.
*   **`Renderer`**: Handles Jinja2 template rendering.

### Generators (`src/litestar_start/generators/`)
*   **`ProjectOrchestrator`**: The main conductor. It initializes the context, loads the appropriate backend/frontend generators, and executes them in order.
*   **`Registry`**: A central place where backends and frontends are registered.

### Backends & Frontends
Each supported framework has its own directory in `src/litestar_start/backends/` or `src/litestar_start/frontends/`.

**Structure of a Backend/Frontend Module:**
*   `generator.py`: Contains a class inheriting from `BaseGenerator`. It defines the logic for copying files, rendering templates, and modifying configuration.
*   `templates/`: Contains the actual source files (using Jinja2 syntax) that will be generated.
*   `plugins/`: (Optional) Logic for specific integrations (like SQLAlchemy setup).

## Adding a New Framework

To add a new backend (e.g., Flask) or frontend (e.g., Vue):

1.  **Create the directory**: `src/litestar_start/backends/flask/`
2.  **Create `generator.py`**:
    ```python
    from litestar_start.backends.base import BackendGenerator

    class FlaskGenerator(BackendGenerator):
        def generate(self):
            # Logic to render templates
            self.render_template("app/main.py.jinja", "app/main.py")
    ```
3.  **Add Templates**: Add your `.jinja` files in `src/litestar_start/backends/flask/templates/`.
4.  **Register it**:
    Edit `src/litestar_start/generators/loader.py` (or wherever registration happens) to ensure your generator is loaded and registered in `GeneratorRegistry`.

## Release Process

1.  Ensure all changes are committed.
2.  Run the release script:
    ```bash
    make release
    ```
    This prepares the release, syncs dependencies, and updates the lockfile.
