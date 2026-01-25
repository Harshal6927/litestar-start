# Project Patterns

> Consolidated learnings and patterns from all tracks.
> This file is the single source of truth for project conventions.

## Code Conventions

- {Convention 1}
- {Convention 2}

## Architecture Patterns

- {Pattern 1}
- {Pattern 2}

## Gotchas & Warnings

- {Gotcha 1}
- {Gotcha 2}

## Testing Patterns

- {Pattern 1}

## Context for AI Assistants

- {Important context}

## [2026-01-24] Patterns from refine-cli-structure-and-improve-plugin-discovery-logic

### Code Conventions
- Use a `Plugin` Protocol to define a strict interface for extensions.
- Automatically generate snake_case IDs from CamelCase class names to maintain template variable consistency.
- Use `pkgutil` and `importlib` for dynamic module discovery in a specific directory.

### Architecture
- Decouple CLI orchestration from specific plugin logic by using a discovery mechanism.
- Use post-generation hooks in plugins to handle specialized setup tasks.
