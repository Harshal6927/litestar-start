# ruff: noqa: PLR6301
"""Unit tests for utility functions."""

from pathlib import Path

from src.utils import (
    get_package_dir,
    get_template_env,
    slugify,
    validate_project_name,
    write_file,
)


class TestGetPackageDir:
    """Tests for get_package_dir function."""

    def test_returns_path(self) -> None:
        """Verify get_package_dir returns a Path object."""
        result = get_package_dir()
        assert isinstance(result, Path)

    def test_returns_src_directory(self) -> None:
        """Verify get_package_dir returns the src directory."""
        result = get_package_dir()
        assert result.name == "src"
        assert result.exists()
        assert result.is_dir()

    def test_contains_expected_files(self) -> None:
        """Verify get_package_dir contains expected module files."""
        result = get_package_dir()
        assert (result / "__init__.py").exists()
        assert (result / "models.py").exists()
        assert (result / "utils.py").exists()


class TestGetTemplateEnv:
    """Tests for get_template_env function."""

    def test_returns_environment(self, tmp_path: Path) -> None:
        """Verify get_template_env returns a Jinja2 Environment."""
        env = get_template_env(tmp_path)
        assert env is not None
        assert hasattr(env, "get_template")

    def test_env_can_load_template(self, tmp_path: Path) -> None:
        """Verify the environment can load templates."""
        # Create a simple template
        template_file = tmp_path / "test.txt"
        template_file.write_text("Hello {{ name }}")

        env = get_template_env(tmp_path)
        template = env.get_template("test.txt")
        result = template.render(name="World")
        assert result == "Hello World"

    def test_env_preserves_trailing_newline(self, tmp_path: Path) -> None:
        """Verify environment preserves trailing newlines."""
        template_file = tmp_path / "test.txt"
        template_file.write_text("Line 1\n")

        env = get_template_env(tmp_path)
        template = env.get_template("test.txt")
        result = template.render()
        assert result == "Line 1\n"

    def test_env_trim_blocks(self, tmp_path: Path) -> None:
        """Verify environment trims blocks correctly."""
        template_file = tmp_path / "test.txt"
        template_file.write_text("{% if true %}\nContent\n{% endif %}")

        env = get_template_env(tmp_path)
        template = env.get_template("test.txt")
        result = template.render()
        # With trim_blocks=True and lstrip_blocks=True, should be clean
        assert "Content" in result


class TestSlugify:
    """Tests for slugify function."""

    def test_lowercase_conversion(self) -> None:
        """Verify slugify converts to lowercase."""
        assert slugify("MyProject") == "myproject"
        assert slugify("ALLCAPS") == "allcaps"

    def test_replace_hyphens(self) -> None:
        """Verify slugify replaces hyphens with underscores."""
        assert slugify("my-project") == "my_project"
        assert slugify("multi-hyphen-name") == "multi_hyphen_name"

    def test_replace_spaces(self) -> None:
        """Verify slugify replaces spaces with underscores."""
        assert slugify("my project") == "my_project"
        assert slugify("multiple word name") == "multiple_word_name"

    def test_remove_special_characters(self) -> None:
        """Verify slugify removes special characters."""
        assert slugify("my@project") == "myproject"
        assert slugify("test!project#name") == "testprojectname"
        assert slugify("name$with%symbols") == "namewithsymbols"

    def test_digit_prefix(self) -> None:
        """Verify slugify adds underscore prefix if starts with digit."""
        assert slugify("123project") == "_123project"
        assert slugify("42") == "_42"

    def test_empty_string(self) -> None:
        """Verify slugify handles empty string."""
        assert not slugify("")

    def test_special_chars_only(self) -> None:
        """Verify slugify returns empty string for special chars only."""
        assert not slugify("@#$%")
        assert not slugify("!!!")

    def test_mixed_case_spaces_hyphens(self) -> None:
        """Verify slugify handles mixed case, spaces, and hyphens."""
        assert slugify("My-Cool Project") == "my_cool_project"
        assert slugify("The-Great App Name") == "the_great_app_name"

    def test_unicode_characters(self) -> None:
        """Verify slugify strips unicode characters."""
        assert slugify("café") == "caf"
        assert slugify("naïve") == "nave"

    def test_consecutive_hyphens(self) -> None:
        """Verify slugify collapses consecutive hyphens to single underscore."""
        assert slugify("my--project") == "my_project"
        assert slugify("a---b") == "a_b"

    def test_consecutive_spaces(self) -> None:
        """Verify slugify collapses consecutive spaces to single underscore."""
        assert slugify("my   project") == "my_project"

    def test_mixed_consecutive_separators(self) -> None:
        """Verify slugify collapses mixed hyphens/spaces to single underscore."""
        assert slugify("my - project") == "my_project"
        assert slugify("a - - b") == "a_b"

    def test_leading_trailing_separators(self) -> None:
        """Verify slugify handles leading/trailing hyphens and spaces."""
        assert slugify("-project-") == "_project_"
        assert slugify(" project ") == "_project_"

    def test_underscores_preserved(self) -> None:
        """Verify slugify preserves existing underscores."""
        assert slugify("my_project") == "my_project"


class TestValidateProjectName:
    """Tests for validate_project_name function."""

    def test_valid_name(self) -> None:
        """Verify validate_project_name returns None for valid names."""
        assert validate_project_name("my-project") is None
        assert validate_project_name("MyProject") is None
        assert validate_project_name("a") is None
        assert validate_project_name("x" * 50) is None

    def test_empty_name(self) -> None:
        """Verify validate_project_name rejects empty string."""
        error = validate_project_name("")
        assert error is not None
        assert "empty" in error.lower()

    def test_too_long(self) -> None:
        """Verify validate_project_name rejects names over 50 chars."""
        error = validate_project_name("x" * 51)
        assert error is not None
        assert "50" in error

    def test_no_letters(self) -> None:
        """Verify validate_project_name rejects names with no letters."""
        # Note: "123" becomes "_123" after slugification, which is valid
        # Only pure special chars without any alphanumerics will fail
        error = validate_project_name("@#$%")
        assert error is not None
        assert "letter" in error.lower()

    def test_single_letter(self) -> None:
        """Verify validate_project_name accepts single letter."""
        assert validate_project_name("a") is None
        assert validate_project_name("Z") is None

    def test_max_length_boundary(self) -> None:
        """Verify validate_project_name at exact 50-char boundary."""
        assert validate_project_name("x" * 49) is None
        assert validate_project_name("x" * 50) is None
        error = validate_project_name("x" * 51)
        assert error is not None
        assert "50" in error

    def test_numeric_only_name(self) -> None:
        """Verify validate_project_name accepts numeric-only names (slugified to _123)."""
        assert validate_project_name("123") is None


class TestWriteFile:
    """Tests for write_file function."""

    def test_writes_file(self, tmp_path: Path) -> None:
        """Verify write_file writes content to file."""
        file_path = tmp_path / "test.txt"
        content = "Hello, World!"
        write_file(file_path, content)
        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == content

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Verify write_file creates parent directories."""
        file_path = tmp_path / "parent" / "child" / "test.txt"
        content = "Nested content"
        write_file(file_path, content)
        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == content

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        """Verify write_file overwrites existing files."""
        file_path = tmp_path / "test.txt"
        write_file(file_path, "First content")
        write_file(file_path, "Second content")
        assert file_path.read_text(encoding="utf-8") == "Second content"

    def test_utf8_encoding(self, tmp_path: Path) -> None:
        """Verify write_file uses UTF-8 encoding."""
        file_path = tmp_path / "test.txt"
        content = "Hello 世界 🌍"
        write_file(file_path, content)
        assert file_path.read_text(encoding="utf-8") == content
