"""Module for loading prompt templates from markdown files.

This module provides functionality to load prompt templates stored as markdown
files for use in chat agents and other LLM applications.
"""

from pathlib import Path

from utils.logger import Logger

logger = Logger().get_logger()


class PromptTemplateLoader:
    """Loads prompt templates from markdown files.

    Attributes:
        prompt_template_directory: Path to the directory containing prompt templates.
    """

    prompt_template_directory = Path(__file__).parent

    def load_template(self, file_name: str) -> str:
        """Loads a prompt template from a markdown file.

        Args:
            file_name: Name of the markdown file to load.

        Returns:
            The content of the template file as a string.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            PermissionError: If there are insufficient permissions to read the file.
            Exception: For any other unexpected errors during file reading.
        """
        try:
            file_path = self.prompt_template_directory / file_name
            return file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except PermissionError:
            logger.error(f"Permission denied: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading template: {file_path} - {e}")
            raise


if __name__ == "__main__":
    file_name = "chat_agent_prompt_template_system.md"
    ptl = PromptTemplateLoader()

    logger.info(ptl.load_template(file_name))
