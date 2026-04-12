# Dead Code Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove dead code and fix inconsistencies in `src/utils.py` and `src/models.py` (audit items #21-24).

**Architecture:** Remove two unused functions (`create_directory`, `render_template`), unify slug generation by making `ProjectConfig.slug` delegate to `slugify()`, and remove a redundant validation check. Each change is small and self-contained.

**Tech Stack:** Python 3.13+, pytest, msgspec

---

## File Map

- Modify: `src/utils.py` — remove `create_directory()` (lines 86-88), remove `render_template()` (lines 97-110), remove redundant length check in `validate_project_name()` (lines 75-76)
- Modify: `src/models.py` — change `ProjectConfig.slug` property (line 47) to delegate to `slugify()`
- Modify: `tests/test_utils.py` — remove `TestCreateDirectory` class (lines 162-184), remove `TestRenderTemplate` class (lines 221-252), add boundary tests for `slugify()`
- Modify: `tests/test_models.py` — update `slug` tests to verify special char handling

---

### Task 1: Remove `create_directory()` and its tests

`create_directory()` at `src/utils.py:86-88` is never called in production code. `write_file()` creates parent directories itself, and `ProjectGenerator.generate()` uses `mkdir` directly.

**Files:**
- Modify: `src/utils.py:86-88`
- Modify: `tests/test_utils.py:6-14` (imports), `tests/test_utils.py:162-184` (test class)

- [ ] **Step 1: Remove `TestCreateDirectory` test class from `tests/test_utils.py`**

Remove lines 162-184 (the entire `TestCreateDirectory` class) and remove `create_directory` from the import statement on line 7.

The import block should change from:
```python
from src.utils import (
    create_directory,
    get_package_dir,
    get_template_env,
    render_template,
    slugify,
    validate_project_name,
    write_file,
)
```
to:
```python
from src.utils import (
    get_package_dir,
    get_template_env,
    render_template,
    slugify,
    validate_project_name,
    write_file,
)
```

(Note: `render_template` will be removed in Task 2. Leave it for now.)

- [ ] **Step 2: Run tests to verify removal doesn't break anything**

Run: `pytest tests/test_utils.py -v`
Expected: All remaining tests PASS. `TestCreateDirectory` tests no longer appear.

- [ ] **Step 3: Remove `create_directory()` function from `src/utils.py`**

Remove lines 86-88:
```python
def create_directory(path: Path) -> None:
    """Create a directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
```

Also remove the blank line (line 89) following it.

- [ ] **Step 4: Run full test suite to verify nothing depends on `create_directory`**

Run: `pytest -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/utils.py tests/test_utils.py
git commit -m "refactor: remove unused create_directory function"
```

---

### Task 2: Remove `render_template()` and its tests

`render_template()` at `src/utils.py:97-110` (after Task 1 removal, line numbers shift) is never called in production code. All template rendering is done directly via `env.get_template(name).render(**context)` in `src/Litestar/generator.py`.

**Files:**
- Modify: `src/utils.py` (remove the `render_template` function)
- Modify: `tests/test_utils.py` (remove `TestRenderTemplate` class and its import)

- [ ] **Step 1: Remove `TestRenderTemplate` test class from `tests/test_utils.py`**

Remove the entire `TestRenderTemplate` class (was lines 221-252 before Task 1; after Task 1, it's the last class in the file). Also remove `render_template` from the import statement.

The import block should now be:
```python
from src.utils import (
    get_package_dir,
    get_template_env,
    slugify,
    validate_project_name,
    write_file,
)
```

- [ ] **Step 2: Run tests to verify removal doesn't break anything**

Run: `pytest tests/test_utils.py -v`
Expected: All remaining tests PASS. `TestRenderTemplate` tests no longer appear.

- [ ] **Step 3: Remove `render_template()` function from `src/utils.py`**

Remove the entire function (was lines 97-110, now shifted after Task 1):
```python
def render_template(env: Environment, template_name: str, context: dict) -> str:
    """Render a Jinja2 template with the given context.

    Args:
        env: The Jinja2 environment.
        template_name: The name of the template to render.
        context: The context dictionary to render the template with.

    Returns:
        The rendered template string.

    """
    template = env.get_template(template_name)
    return template.render(**context)
```

Also remove the now-unused `Environment` import from the top of the file. The imports should become:
```python
import re
from pathlib import Path

from jinja2 import FileSystemLoader, select_autoescape
```

Wait — `get_template_env` still returns `Environment` and uses `Environment(...)`. Check: `get_template_env` creates `Environment(loader=FileSystemLoader(...), ...)` so the import is still needed. Keep the `Environment` import.

Actually, looking at the code: `get_template_env` returns `Environment` and constructs it. So `Environment` IS still needed. Do NOT remove the `Environment` import.

- [ ] **Step 4: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/utils.py tests/test_utils.py
git commit -m "refactor: remove unused render_template function"
```

---

### Task 3: Unify slug generation — make `ProjectConfig.slug` use `slugify()`

`ProjectConfig.slug` (at `src/models.py:47`) uses inline logic:
```python
return self.name.lower().replace("-", "_").replace(" ", "_")
```
This is buggy — it doesn't handle special characters like `@#$`, consecutive hyphens/spaces, or digit-prefixed names. Meanwhile, `slugify()` in `src/utils.py` handles all of these correctly. Make `slug` delegate to `slugify()`.

**Files:**
- Modify: `src/models.py:2-3` (add import), `src/models.py:44-47` (change slug property)
- Modify: `tests/test_models.py` (add tests for special char slug handling)

- [ ] **Step 1: Write failing tests for `ProjectConfig.slug` with special characters**

Add these tests to the existing `TestProjectConfigSlug` class in `tests/test_models.py`. First, find the class — it should contain tests like `test_slug_basic`, `test_slug_with_hyphens`, etc.

Add the following test methods to that class:

```python
def test_slug_removes_special_characters(self) -> None:
    """Verify slug removes special characters like @, #, $."""
    config = ProjectConfig(
        name="my@project#name",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=[],
        docker=False,
        docker_infra=False,
    )
    assert config.slug == "myprojectname"

def test_slug_handles_digit_prefix(self) -> None:
    """Verify slug adds underscore prefix for digit-starting names."""
    config = ProjectConfig(
        name="123app",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=[],
        docker=False,
        docker_infra=False,
    )
    assert config.slug == "_123app"

def test_slug_handles_consecutive_separators(self) -> None:
    """Verify slug collapses consecutive hyphens/spaces to single underscore."""
    config = ProjectConfig(
        name="my--project  name",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=[],
        docker=False,
        docker_infra=False,
    )
    assert config.slug == "my_project_name"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models.py -k "test_slug_removes_special or test_slug_handles_digit or test_slug_handles_consecutive" -v`
Expected: FAIL — the current inline logic doesn't remove special chars, doesn't handle digit prefix, and doesn't collapse consecutive separators.

- [ ] **Step 3: Update `ProjectConfig.slug` to delegate to `slugify()`**

In `src/models.py`, add the import at the top (after `import msgspec`):

```python
from src.utils import slugify
```

Then change the `slug` property from:
```python
@property
def slug(self) -> str:
    """Return project name as a valid Python package name."""
    return self.name.lower().replace("-", "_").replace(" ", "_")
```
to:
```python
@property
def slug(self) -> str:
    """Return project name as a valid Python package name."""
    return slugify(self.name)
```

- [ ] **Step 4: Run all tests to verify everything passes**

Run: `pytest -v`
Expected: All tests PASS, including the new special character tests and all existing slug tests.

- [ ] **Step 5: Commit**

```bash
git add src/models.py tests/test_models.py
git commit -m "fix: unify slug generation by delegating ProjectConfig.slug to slugify()"
```

---

### Task 4: Remove redundant length check in `validate_project_name()`

In `src/utils.py`, `validate_project_name()` has this code:
```python
if not name:
    return "Project name cannot be empty"
if len(name) < MIN_PROJECT_NAME_LENGTH:
    return f"Project name must be at least {MIN_PROJECT_NAME_LENGTH} characters"
```
Since `MIN_PROJECT_NAME_LENGTH = 1`, any non-empty string has `len >= 1`, so the second check is unreachable after the first. Remove it.

**Files:**
- Modify: `src/utils.py` (remove lines 75-76 in current state)

- [ ] **Step 1: Verify the redundancy by checking existing test coverage**

Run: `pytest tests/test_utils.py::TestValidateProjectName -v`
Expected: All validation tests PASS. The `test_empty_name` test covers the empty case.

- [ ] **Step 2: Remove the redundant length check**

In `src/utils.py`, change `validate_project_name` from:
```python
def validate_project_name(name: str) -> str | None:
    """Validate project name. Returns error message or None if valid.

    Args:
        name: The project name to validate.

    Returns:
        An error message if the name is invalid, otherwise None.

    """
    if not name:
        return "Project name cannot be empty"
    if len(name) < MIN_PROJECT_NAME_LENGTH:
        return f"Project name must be at least {MIN_PROJECT_NAME_LENGTH} characters"
    if len(name) > MAX_PROJECT_NAME_LENGTH:
        return f"Project name must be less than {MAX_PROJECT_NAME_LENGTH} characters"
    # Check if slugified name is valid
    slug = slugify(name)
    if not slug:
        return "Project name must contain at least one letter"
    return None
```
to:
```python
def validate_project_name(name: str) -> str | None:
    """Validate project name. Returns error message or None if valid.

    Args:
        name: The project name to validate.

    Returns:
        An error message if the name is invalid, otherwise None.

    """
    if not name:
        return "Project name cannot be empty"
    if len(name) > MAX_PROJECT_NAME_LENGTH:
        return f"Project name must be less than {MAX_PROJECT_NAME_LENGTH} characters"
    # Check if slugified name is valid
    slug = slugify(name)
    if not slug:
        return "Project name must contain at least one letter"
    return None
```

Also remove the now-unused `MIN_PROJECT_NAME_LENGTH` constant from line 8. Keep `MAX_PROJECT_NAME_LENGTH`.

- [ ] **Step 3: Run all tests**

Run: `pytest -v`
Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git add src/utils.py
git commit -m "refactor: remove redundant MIN_PROJECT_NAME_LENGTH check in validate_project_name"
```
