# CI Test Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a GitHub Actions CI workflow that runs pytest on push and PR, closing the gap where only linting runs in CI (audit item #57).

**Architecture:** Create a new `test.yml` workflow alongside the existing `lint.yml`. The workflow installs dependencies with `uv`, runs `pytest`, and reports results. Keep it simple — single Python version (3.13), single OS (ubuntu-latest), matching the existing lint workflow style.

**Tech Stack:** GitHub Actions, uv, pytest, Python 3.13

---

## File Map

- Create: `.github/workflows/test.yml` — new CI workflow for running tests

---

### Task 1: Create `.github/workflows/test.yml`

**Files:**
- Create: `.github/workflows/test.yml`

- [ ] **Step 1: Create the workflow file**

Create `.github/workflows/test.yml` with:

```yaml
name: Test

on:
    push:
        branches:
            - main
    pull_request:

concurrency: test-${{ github.sha }}

jobs:
    test:
        runs-on: ubuntu-latest

        env:
            PYTHON_VERSION: "3.13"

        steps:
            - name: Checkout repository
              uses: actions/checkout@v6

            - name: Install uv
              uses: astral-sh/setup-uv@v6

            - name: Set up Python ${{ env.PYTHON_VERSION }}
              uses: actions/setup-python@v6
              with:
                  python-version: ${{ env.PYTHON_VERSION }}

            - name: Install dependencies
              run: uv sync

            - name: Run tests
              run: uv run pytest -v
```

- [ ] **Step 2: Validate YAML syntax**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml'))"
```

If `pyyaml` is not installed, just verify manually that the YAML is valid by checking indentation.

Alternatively, use:
```bash
python -c "
import json, pathlib
# Simple YAML validation: check it's valid text with expected keys
content = pathlib.Path('.github/workflows/test.yml').read_text()
assert 'name: Test' in content
assert 'pytest' in content
print('YAML content looks valid')
"
```

Expected: No errors.

- [ ] **Step 3: Verify test suite passes locally**

Run: `pytest -v`
Expected: All tests PASS. This confirms the workflow will succeed when CI runs it.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/test.yml
git commit -m "ci: add GitHub Actions workflow for running pytest"
```
