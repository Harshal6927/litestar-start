# Learnings: refine-cli-structure-and-improve-plugin-discovery-logic

> Append-only log of discoveries during implementation.
> Format: [timestamp] - Phase/Task - Learning

## Session Log

### [2026-01-24] - Phase 1 Task 1: Analyze current CLI structure
- **Findings:**
    - `src/cli.py` is monolithic. `ask_plugins` and `run_post_generation_setup` have hardcoded plugin logic.
    - `src/generator.py` is a simple orchestrator but `src/Litestar/generator.py` has hardcoded plugin flags in `_get_template_context`.
    - Plugins are integrated via two mechanisms:
        1. Directory-based template rendering (`Plugins/<Name>/Templates`).
        2. Boolean flags in template context used for conditional logic in base templates.
    - `src/models.py` contains the `Plugin` enum and helper properties on `ProjectConfig`.

- **Coupling Points:**
    - `Plugin` enum in `src/models.py`.
    - `ask_plugins` in `src/cli.py`.
    - `run_post_generation_setup` in `src/cli.py` (specifically for LitestarVite).
    - `_get_template_context` in `src/Litestar/generator.py`.
    - `ProjectConfig` helper properties in `src/models.py`.

## Patterns Discovered
- Directory-based plugin structure in `src/Litestar/Plugins/`.
- Automatic plugin discovery using `pkgutil` and `importlib`.
- Using a `Plugin` Protocol to define a strict interface for extensions.
- Automatic snake_case ID generation from CamelCase class names.

## Gotchas & Warnings
- When using `replace` with `# ...` or other placeholders, it can break indentation if not careful. Always provide full context.
- Templates often depend on specific variable names (e.g., `advanced_alchemy`). The plugin system must ensure these names are consistent with what templates expect.
- `pkgutil.iter_modules` requires a list of strings (paths), not just a single Path object.

## Decisions Made
- Replaced `Plugin` enum with `list[str]` in `ProjectConfig` for dynamic extensibility.
- Added `post_generate` hook to `Plugin` class to handle plugin-specific setup (e.g., running CLI commands in the generated project).
- Decided to automatically lowercase and snake_case plugin IDs based on class names to match existing template variable conventions.

## Gotchas & Warnings
[Pitfalls to avoid in similar work]

## Decisions Made
[Key decisions and their rationale]
