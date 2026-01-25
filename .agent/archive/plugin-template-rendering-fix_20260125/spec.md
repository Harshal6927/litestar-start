# Plugin Template Rendering Fix

## Overview
After refactoring the plugin system, an issue was identified where plugin templates (specifically those within nested folders like `lib` or `models`) are not being rendered into the final project. This is primarily caused by a case-sensitivity mismatch: the generator searches for plugin directories using snake_case IDs (e.g., `advanced_alchemy`), while the actual directories on disk use PascalCase (e.g., `AdvancedAlchemy`). Additionally, the generator needs to ensure that it correctly handles situations where target folders already exist in the generated project.

## Research Reference
No prior research conducted

## Functional Requirements
### Must Have
- [ ] Correctly locate plugin `Templates` directories by mapping plugin IDs to their source directory names.
- [ ] Recursively render all `.jinja` files within a plugin's `Templates` folder, preserving the internal directory structure.
- [ ] Create missing directories in the output path as needed during template rendering.
- [ ] If a target directory already exists (e.g., `lib/`), render templates into that existing directory without error.

### Should Have
- [ ] Improved robustness in `LitestarGenerator` to handle various plugin directory naming conventions.

## Non-Functional Requirements
- **Performance:** Rendering logic should remain efficient and not introduce significant overhead.
- **Maintainability:** The solution should leverage the existing `_render_templates` abstraction.

## Technical Approach
### Recommended Implementation
1. **Plugin Protocol Update:** Modify the `Plugin` protocol and `BasePlugin` in `src/plugin.py` to include a `path` property that stores the absolute path to the plugin's directory.
2. **Discovery Logic:** Update `discover_plugins` in `src/plugin.py` to set the `path` property during discovery.
3. **Generator Fix:** In `src/Litestar/generator.py`, update `_generate_plugins` to iterate through the discovered `self.plugins` objects (which now have the correct path) instead of building the path from `config.plugins` strings.
4. **Recursive Rendering:** Ensure `_render_templates` correctly joins paths and creates parents for the output files.

### Libraries/APIs to Use
- `pathlib.Path` for cross-platform path handling.
- `jinja2.Environment` for template rendering.

### Files to Modify
- `src/plugin.py`
- `src/Litestar/generator.py`

## Acceptance Criteria
- [ ] Running `litestar-start` with the `advanced_alchemy` plugin generates a `models/` directory if missing.
- [ ] Rendered templates (e.g., `models/users.py`) are present in the final project.
- [ ] Files inside an existing `lib/` directory are correctly generated from plugin templates (e.g., `lib/services.py`).
- [ ] The generated project structure matches the one defined in the plugin's `Templates` folder.

## Out of Scope
- Changing the plugin ID system or renaming existing plugin directories.
- Modification of actual template contents.

## Dependencies
### Internal Dependencies
- None

## Risk Assessment
### Identified Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Path resolution errors on Windows | Low | Medium | Use `pathlib` for all path manipulations. |
| Overwriting existing files silently | Med | Medium | Ensure `write_file` behavior matches expectations (currently it overwrites). |

### Recovery Strategy
**Rollback Trigger:** Generation failures or corrupted project structures.
**Rollback Steps:**
1. Revert changes to `src/plugin.py`.
2. Revert changes to `src/Litestar/generator.py`.

**Safe Checkpoints:**
- After Phase 1: Plugin discovery updated and verified.
- After Phase 2: Generation logic updated and tested.

## Open Questions
- None
