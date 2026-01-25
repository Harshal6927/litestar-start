# Specification: Refine CLI structure and improve plugin discovery logic

## 1. Overview
This PRD focuses on refining the internal structure of the CLI to better support modularity and improving the logic used to discover and load plugins. The goal is to make the codebase more maintainable and extensible.

## 2. Goals
- Refactor `src/cli.py` to be cleaner and more focused on orchestration.
- Implement a robust plugin discovery mechanism in `src/generator.py` or a new module.
- Ensure all changes adhere to the project's strict typing and linting rules.

## 3. User Stories
- As a developer, I want to easily add new plugins without modifying the core CLI logic.
- As a maintainer, I want the CLI code to be easy to read and debug.

## 4. Technical Implementation
- **CLI Refactoring:** Break down the monolithic CLI function into smaller, reusable components.
- **Plugin Discovery:** Use Python's `pkgutil` or `importlib` to dynamically discover plugins in the `src/Litestar/Plugins` directory.
- **Typing:** Ensure all new code is fully typed and passes `ty` checks.

## 5. Non-Functional Requirements
- **Performance:** Plugin discovery should not noticeably slow down the CLI startup.
- **Reliability:** The CLI should handle malformed plugins gracefully without crashing.
