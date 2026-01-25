# Implementation Plan - Plugin Template Rendering Fix

## Phase 1: Plugin Metadata and Discovery
<!-- execution: sequential -->

- [x] Task: Create unit tests for updated plugin discovery logic
    - [ ] Define test cases in `tests/test_plugin.py` to verify that `path` is correctly set.
- [x] Task: Update Plugin system in `src/plugin.py`
    - [ ] Add `path: Path` property to `Plugin` protocol.
    - [ ] Add `path: Path` property to `BasePlugin`.
    - [ ] Update `discover_plugins` to set the absolute directory path for each discovered plugin instance.
- [x] Task: Verify Phase 1 passing
    - [ ] Run `pytest tests/test_plugin.py`.
- [x] Task: Checkpoint - Verify Phase 1 complete and create recovery point [checkpoint: 856d379]
- [x] Task: Flow - User Manual Verification 'Plugin Metadata and Discovery' (Protocol in workflow.md)

## Phase 2: Litestar Generator Logic
<!-- execution: sequential -->

- [ ] Task: Create integration tests for plugin template generation
    - [ ] Add test cases in `tests/test_generator.py` that check for nested folder creation and template rendering from plugins.
- [ ] Task: Refactor `LitestarGenerator` in `src/Litestar/generator.py`
    - [ ] Update `_generate_plugins` to iterate over plugin objects and use their `path` property to locate `Templates/`.
    - [ ] Ensure `_render_templates` correctly handles sub-directories and output path construction.
- [ ] Task: Verify Phase 2 passing
    - [ ] Run `pytest tests/test_generator.py`.
- [ ] Task: Checkpoint - Verify Phase 2 complete and create recovery point
- [ ] Task: Flow - User Manual Verification 'Litestar Generator Logic' (Protocol in workflow.md)

## Phase 3: Integration and Quality
<!-- execution: sequential -->

- [ ] Task: End-to-end verification
    - [ ] Run a full generation cycle using the CLI locally.
    - [ ] Verify `lib/` and `models/` folders in the generated project.
- [ ] Task: Quality Gate
    - [ ] Run `make lint` to ensure no regressions in code style or types.
- [ ] Task: Checkpoint - Verify Phase 3 complete and create recovery point
- [ ] Task: Flow - User Manual Verification 'Integration and Quality' (Protocol in workflow.md)
