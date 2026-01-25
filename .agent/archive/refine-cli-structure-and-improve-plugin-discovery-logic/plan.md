# Implementation Plan - Refine CLI structure and improve plugin discovery logic

## Phase 1: Analysis & Design
- [x] Task: Analyze current CLI structure in `src/cli.py` and plugin handling in `src/generator.py`.
    - [ ] Subtask: Read and document existing control flow.
    - [ ] Subtask: Identify coupling points between CLI and specific plugins.
- [x] Task: Design the new plugin interface and discovery mechanism.
    - [ ] Subtask: Draft a `Plugin` protocol/base class.
    - [ ] Subtask: Prototype discovery logic using `importlib`.
- [x] Task: Flow - User Manual Verification 'Analysis - [ ] Task: Flow - User Manual Verification 'Analysis & Design' Design' (Protocol in workflow.md)

## Phase 2: Refactoring Core Logic
- [ ] Task: Refactor `src/generator.py` to use the new plugin discovery logic.
    - [ ] Subtask: Write tests for plugin discovery (mocking the filesystem).
    - [ ] Subtask: Implement the discovery function.
- [ ] Task: Refactor `src/cli.py` to utilize the new generator capabilities.
    - [ ] Subtask: Remove hardcoded plugin references.
    - [ ] Subtask: Update `ProjectConfig` model if necessary.
- [x] Task: Flow - User Manual Verification 'Refactoring Core Logic' (Protocol in workflow.md)

## Phase 3: Verification & Cleanup
- [x] Task: Verify all existing plugins are correctly discovered and loaded.
    - [ ] Subtask: Run the CLI and generate a project with all options.
    - [ ] Subtask: Manually inspect the generated project.
- [x] Task: Run full linting and type checking suite.
    - [ ] Subtask: Run `make lint`.
- [x] Task: Flow - User Manual Verification 'Verification - [ ] Task: Flow - User Manual Verification 'Verification & Cleanup' Cleanup' (Protocol in workflow.md)
