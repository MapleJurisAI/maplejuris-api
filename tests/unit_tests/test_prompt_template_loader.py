"""Tests for PromptTemplateLoader class."""

import pytest

from prompt_templates.prompt_template_loader import PromptTemplateLoader


class TestPromptTemplateLoader:
    """Test suite for PromptTemplateLoader class."""

    @pytest.fixture
    def loader(self):
        """Fixture to create a PromptTemplateLoader instance.

        Returns:
            PromptTemplateLoader: An instance of the loader class.
        """
        return PromptTemplateLoader()

    @pytest.fixture
    def tmp_prompt_template_file(self, tmp_path):
        """Fixture to create a temporary prompt template file.

        Args:
            tmp_path: Pytest fixture providing temporary directory path.

        Returns:
            Path: Path object pointing to the created temporary file.
        """
        prompt_template = "You are a test helper"
        prompt_template_file = tmp_path / "test_prompt_template.md"
        prompt_template_file.write_text(prompt_template, encoding="utf-8")
        return prompt_template_file

    def test_load_template_success(self, loader, tmp_prompt_template_file, monkeypatch):
        """Test successful loading of a template file.

        Args:
            loader: PromptTemplateLoader instance fixture.
            tmp_prompt_template_file: Temporary template file fixture.
            monkeypatch: Pytest fixture for modifying attributes.
        """
        monkeypatch.setattr(
            loader, "prompt_template_directory", tmp_prompt_template_file.parent
        )
        result = loader.load_template(file_name=tmp_prompt_template_file.name)
        assert result == "You are a test helper"

    def test_load_template_file_not_found(self, loader):
        """Test that FileNotFoundError is raised for non-existent files.

        Args:
            loader: PromptTemplateLoader instance fixture.
        """
        with pytest.raises(FileNotFoundError):
            loader.load_template(file_name="nonexistent_file.md")

    def test_load_template_permission_error(self, loader, tmp_path, monkeypatch):
        """Test that PermissionError is raised when file permissions are denied.

        Args:
            loader: PromptTemplateLoader instance fixture.
            tmp_path: Pytest fixture providing temporary directory path.
            monkeypatch: Pytest fixture for modifying attributes.
        """
        # Create a file with no read permissions
        restricted_file = tmp_path / "restricted.md"
        restricted_file.write_text("test content", encoding="utf-8")
        restricted_file.chmod(0o000)  # Remove all permissions

        # Point loader to temp directory
        monkeypatch.setattr(loader, "prompt_template_directory", tmp_path)

        # Test that PermissionError is raised
        with pytest.raises(PermissionError):
            loader.load_template(file_name="restricted.md")

        # Cleanup - restore permissions
        restricted_file.chmod(0o644)
