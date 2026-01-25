# Learnings

## [2026-01-25] - Plugin Template Rendering Fix

- **Implemented:** Fixed plugin template rendering by correctly resolving plugin directory paths using `pkgutil` module discovery instead of constructing paths from snake_case IDs.
- **Files changed:** `src/plugin.py`, `src/Litestar/generator.py`
- **Learnings:**
  - **Pattern:** Use `pkgutil.iter_modules` results to determine the actual directory name on disk (preserving PascalCase) for resource location, rather than inferring it from class names.
  - **Gotcha:** Generated code might fail type checking (`ty` / `mypy`) if it imports libraries that are not installed in the developer's environment (but are dependencies of the generated project).
