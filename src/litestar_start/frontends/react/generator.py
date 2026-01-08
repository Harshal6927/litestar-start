"""React frontend generator."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from litestar_start.core.utils import ensure_dir, write_file
from litestar_start.frontends.base import FrontendGenerator

if TYPE_CHECKING:
    from pathlib import Path

    from litestar_start.core.base import GeneratorContext


class ReactGenerator(FrontendGenerator):
    """Generator for React frontend projects."""

    @property
    def name(self) -> str:
        """Generator name."""
        return "react"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "React"

    def get_dependencies(self) -> list[str]:
        """Get React dependencies.

        Returns:
            List of npm dependencies.

        """
        return ["react@^18.2.0", "react-dom@^18.2.0"]

    def _generate_package_json(self, frontend_dir: Path, context: GeneratorContext) -> None:
        """Generate package.json for React.

        Args:
            frontend_dir: Frontend directory path.
            context: Generator context.

        """
        package_json = {
            "name": f"{context.project_slug}-frontend",
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
                "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "@vitejs/plugin-react": "^4.2.1",
                "eslint": "^8.55.0",
                "eslint-plugin-react": "^7.33.2",
                "eslint-plugin-react-hooks": "^4.6.0",
                "eslint-plugin-react-refresh": "^0.4.5",
                "vite": "^5.0.0",
            },
        }

        content = json.dumps(package_json, indent=2) + "\n"
        write_file(frontend_dir / "package.json", content)

    def _generate_src_structure(self, frontend_dir: Path, context: GeneratorContext) -> None:
        """Generate React source structure.

        Args:
            frontend_dir: Frontend directory path.
            context: Generator context.

        """
        src_dir = frontend_dir / "src"
        ensure_dir(src_dir)

        # Create App.jsx
        app_content = self._create_app_component(context)
        write_file(src_dir / "App.jsx", app_content)

        # Create main.jsx
        main_content = self._create_main_file()
        write_file(src_dir / "main.jsx", main_content)

        # Create App.css
        css_content = self._create_app_css()
        write_file(src_dir / "App.css", css_content)

        # Create index.html
        html_content = self._create_index_html(context)
        write_file(frontend_dir / "index.html", html_content)

    def _generate_config_files(self, frontend_dir: Path, context: GeneratorContext) -> None:
        """Generate Vite config.

        Args:
            frontend_dir: Frontend directory path.
            context: Generator context.

        """
        vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
})
"""
        write_file(frontend_dir / "vite.config.js", vite_config)

    @staticmethod
    def _create_app_component(context: GeneratorContext) -> str:
        """Create App.jsx component.

        Args:
            context: Generator context.

        Returns:
            App component content.

        """
        return f"""import {{ useState }} from 'react'
import './App.css'

function App() {{
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <header className="App-header">
        <h1>{context.project_name}</h1>
        <p>{context.description}</p>
        <button onClick={{() => setCount((c) => c + 1)}}>
          Count: {{count}}
        </button>
      </header>
    </div>
  )
}}

export default App
"""

    @staticmethod
    def _create_main_file() -> str:
        """Create main.jsx file.

        Returns:
            Main file content.

        """
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""

    @staticmethod
    def _create_app_css() -> str:
        """Create App.css file.

        Returns:
            CSS content.

        """
        return """.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
  color: white;
}

button {
  font-size: 1.2em;
  padding: 0.5em 1em;
  margin: 1em;
  cursor: pointer;
}
"""

    @staticmethod
    def _create_index_html(context: GeneratorContext) -> str:
        """Create index.html file.

        Args:
            context: Generator context.

        Returns:
            HTML content.

        """
        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{context.project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""
