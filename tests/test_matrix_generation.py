"""Permutation matrix verification tests."""

import ast
import re
import shutil
import subprocess
import tomllib
from pathlib import Path
from typing import NamedTuple

import pytest
import yaml

from src.Litestar.generator import LitestarGenerator
from src.models import Database, Framework, MemoryStore, ProjectConfig


def _check_no_jinja_leakage(output_dir: Path) -> None:
    """Verify no rendered files contain stray Jinja tags.

    Args:
        output_dir: Root directory of the generated project.

    """
    jinja_delimiters = ("{%", "%}", "{{", "}}")
    for file_path in output_dir.rglob("*"):
        if file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            for delimiter in jinja_delimiters:
                assert delimiter not in content, (
                    f"Stray Jinja delimiter '{delimiter}' found in {file_path.relative_to(output_dir)}"
                )


def _check_python_ast(output_dir: Path) -> None:
    """Parse all generated Python files with ast.parse to guarantee valid syntax.

    Args:
        output_dir: Root directory of the generated project.

    """
    for file_path in output_dir.rglob("*.py"):
        content = file_path.read_text(encoding="utf-8")
        try:
            ast.parse(content, filename=str(file_path))
        except SyntaxError as err:
            pytest.fail(f"Syntax error in generated file {file_path.relative_to(output_dir)}: {err}")


def _check_toml_configs(output_dir: Path) -> None:
    """Parse all generated TOML files using tomllib.loads.

    Args:
        output_dir: Root directory of the generated project.

    """
    for file_path in output_dir.rglob("*.toml"):
        content = file_path.read_text(encoding="utf-8")
        try:
            parsed = tomllib.loads(content)
            assert isinstance(parsed, dict)
            assert "project" in parsed, f"Missing [project] section in {file_path.relative_to(output_dir)}"
        except tomllib.TOMLDecodeError as err:
            pytest.fail(f"TOML decode error in {file_path.relative_to(output_dir)}: {err}")


def _check_yaml_configs(output_dir: Path) -> None:
    """Parse all generated YAML files using yaml.safe_load.

    Args:
        output_dir: Root directory of the generated project.

    """
    for file_path in output_dir.rglob("*"):
        if file_path.suffix in {".yaml", ".yml"} and file_path.is_file():
            content = file_path.read_text(encoding="utf-8")
            try:
                parsed = yaml.safe_load(content)
                assert parsed is not None, f"YAML file {file_path.relative_to(output_dir)} rendered empty content"
            except yaml.YAMLError as err:
                pytest.fail(f"YAML decode error in {file_path.relative_to(output_dir)}: {err}")


def _check_feature_files(
    output_dir: Path,
    expected_files: list[str],
    forbidden_files: list[str],
) -> None:
    """Verify presence of expected files and absence of forbidden/empty stub files.

    Args:
        output_dir: Root directory of the generated project.
        expected_files: Relative paths that must exist.
        forbidden_files: Relative paths that must not exist.

    """
    for rel_path in expected_files:
        target = output_dir / rel_path
        assert target.exists(), f"Expected file '{rel_path}' was not generated"

    for rel_path in forbidden_files:
        target = output_dir / rel_path
        assert not target.exists(), f"Forbidden file '{rel_path}' should not have been generated"


def test_matrix_helpers_detect_jinja_leak(tmp_path: Path) -> None:
    """Verify _check_no_jinja_leakage raises AssertionError on stray delimiters.

    Args:
        tmp_path: Pytest temporary directory fixture.

    """
    leaky_file = tmp_path / "leaky.txt"
    leaky_file.write_text("Hello {{ name }}", encoding="utf-8")
    with pytest.raises(AssertionError, match=re.escape("Stray Jinja delimiter '{{'")):
        _check_no_jinja_leakage(tmp_path)


def test_matrix_helpers_detect_ast_syntax_error(tmp_path: Path) -> None:
    """Verify _check_python_ast catches invalid Python syntax.

    Args:
        tmp_path: Pytest temporary directory fixture.

    """
    bad_py = tmp_path / "bad.py"
    bad_py.write_text("def invalid_syntax(:", encoding="utf-8")
    with pytest.raises(pytest.fail.Exception, match="Syntax error"):
        _check_python_ast(tmp_path)


def test_matrix_helpers_detect_toml_error(tmp_path: Path) -> None:
    """Verify _check_toml_configs catches invalid TOML.

    Args:
        tmp_path: Pytest temporary directory fixture.

    """
    bad_toml = tmp_path / "pyproject.toml"
    bad_toml.write_text("[project\nname = 123", encoding="utf-8")
    with pytest.raises(pytest.fail.Exception, match="TOML decode error"):
        _check_toml_configs(tmp_path)


def test_matrix_helpers_detect_yaml_error(tmp_path: Path) -> None:
    """Verify _check_yaml_configs catches invalid YAML.

    Args:
        tmp_path: Pytest temporary directory fixture.

    """
    bad_yaml = tmp_path / "config.yaml"
    bad_yaml.write_text("services: [unclosed list", encoding="utf-8")
    with pytest.raises(pytest.fail.Exception, match="YAML decode error"):
        _check_yaml_configs(tmp_path)


class MatrixScenario(NamedTuple):
    """Specification for a permutation scenario."""

    name: str
    database: Database
    memory_store: MemoryStore
    plugins: list[str]
    docker: bool
    docker_dev_infra: bool
    expected_files: list[str]
    forbidden_files: list[str]


MATRIX_SCENARIOS: list[MatrixScenario] = [
    MatrixScenario(
        name="minimal_api",
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=[],
        docker=False,
        docker_dev_infra=False,
        expected_files=[
            "pyproject.toml",
            "README.md",
            "Makefile",
            ".env.example",
            ".gitignore",
            ".pre-commit-config.yaml",
            "src/backend/app.py",
            "src/backend/config.py",
            "src/backend/settings.py",
            "src/backend/controllers/__init__.py",
            "src/backend/schemas/__init__.py",
            "src/backend/lib/__init__.py",
        ],
        forbidden_files=[
            "src/backend/models/users.py",
            "src/backend/lib/services.py",
            "src/backend/lib/dependencies.py",
            "src/backend/lib/tasks.py",
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.dev-infra.yml",
        ],
    ),
    MatrixScenario(
        name="sqlite_full",
        database=Database.SQLITE,
        memory_store=MemoryStore.NONE,
        plugins=["advanced_alchemy", "litestar_granian"],
        docker=False,
        docker_dev_infra=False,
        expected_files=[
            "pyproject.toml",
            "src/backend/app.py",
            "src/backend/models/users.py",
            "src/backend/lib/services.py",
            "src/backend/lib/dependencies.py",
        ],
        forbidden_files=[
            "src/backend/lib/tasks.py",
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.dev-infra.yml",
        ],
    ),
    MatrixScenario(
        name="postgres_redis",
        database=Database.POSTGRESQL,
        memory_store=MemoryStore.REDIS,
        plugins=["advanced_alchemy", "litestar_saq", "litestar_granian"],
        docker=True,
        docker_dev_infra=True,
        expected_files=[
            "pyproject.toml",
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.dev-infra.yml",
            "src/backend/app.py",
            "src/backend/models/users.py",
            "src/backend/lib/services.py",
            "src/backend/lib/dependencies.py",
            "src/backend/lib/tasks.py",
        ],
        forbidden_files=[],
    ),
    MatrixScenario(
        name="mysql_valkey",
        database=Database.MYSQL,
        memory_store=MemoryStore.VALKEY,
        plugins=["advanced_alchemy", "litestar_saq"],
        docker=True,
        docker_dev_infra=True,
        expected_files=[
            "pyproject.toml",
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.dev-infra.yml",
            "src/backend/app.py",
            "src/backend/models/users.py",
            "src/backend/lib/services.py",
            "src/backend/lib/dependencies.py",
            "src/backend/lib/tasks.py",
        ],
        forbidden_files=[],
    ),
    MatrixScenario(
        name="vite_fullstack",
        database=Database.POSTGRESQL,
        memory_store=MemoryStore.NONE,
        plugins=["advanced_alchemy", "litestar_vite"],
        docker=True,
        docker_dev_infra=True,
        expected_files=[
            "pyproject.toml",
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.dev-infra.yml",
            "src/backend/app.py",
            "src/backend/models/users.py",
            "src/backend/lib/services.py",
            "src/backend/lib/dependencies.py",
        ],
        forbidden_files=[
            "src/backend/lib/tasks.py",
        ],
    ),
]


@pytest.mark.parametrize(
    "scenario",
    MATRIX_SCENARIOS,
    ids=[scenario.name for scenario in MATRIX_SCENARIOS],
)
def test_matrix_generation_permutations(scenario: MatrixScenario, tmp_path: Path) -> None:
    """Validate project generation across permutation matrix scenarios.

    Args:
        scenario: Permutation scenario specification.
        tmp_path: Pytest temporary directory fixture.

    """
    output_dir = tmp_path / scenario.name
    config = ProjectConfig(
        name=f"Test {scenario.name.replace('_', ' ').title()}",
        framework=Framework.LITESTAR,
        database=scenario.database,
        memory_store=scenario.memory_store,
        plugins=scenario.plugins,
        docker=scenario.docker,
        docker_dev_infra=scenario.docker_dev_infra,
    )

    generator = LitestarGenerator(config, output_dir)
    generator.generate()

    # 1. Template Leakage Check
    _check_no_jinja_leakage(output_dir)

    # 2. Python AST & Syntax Validation
    _check_python_ast(output_dir)

    # 3. TOML Configuration Validation
    _check_toml_configs(output_dir)

    # 4. YAML Configuration Validation
    _check_yaml_configs(output_dir)

    # 5. Feature Files Presence & Absence Check
    _check_feature_files(output_dir, scenario.expected_files, scenario.forbidden_files)


@pytest.mark.e2e
def test_matrix_e2e_minimal_installation(tmp_path: Path) -> None:
    """Run full uv sync inside a generated minimal project.

    Guarded with @pytest.mark.e2e for nightly/release runs.

    Args:
        tmp_path: Pytest temporary directory fixture.

    """
    if shutil.which("uv") is None:
        pytest.skip("uv binary not available in environment")

    output_dir = tmp_path / "e2e_minimal"
    config = ProjectConfig(
        name="E2E Minimal",
        framework=Framework.LITESTAR,
        database=Database.NONE,
        memory_store=MemoryStore.NONE,
        plugins=[],
        docker=False,
        docker_dev_infra=False,
    )

    generator = LitestarGenerator(config, output_dir)
    generator.generate()

    # Verify uv sync completes successfully in the generated directory
    sync_result = subprocess.run(
        ["uv", "sync"],  # noqa: S607
        cwd=output_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    assert sync_result.returncode == 0, f"uv sync failed: {sync_result.stderr}"
