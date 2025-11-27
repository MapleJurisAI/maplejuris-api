"""Tests for ChatAgent class."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from agents.chat_agent import ChatAgent
from schemas.chat_agent_schemas import ChatAgentResponse


class TestChatAgent:
    """Test suite for ChatAgent class."""

    @pytest.fixture
    def chat_agent(self):
        """Fixture to create a ChatAgent instance with mocked LLM.

        Returns:
            ChatAgent: An instance of the chat agent with mocked LLM.
        """
        # Mock ChatOpenAI to avoid needing API key
        with patch("agents.chat_agent.ChatOpenAI") as mock_llm:
            mock_llm.return_value = MagicMock()
            agent = ChatAgent(model_name="gpt-4")
            return agent

    def test_initialization_success(self, chat_agent):
        """Test that ChatAgent instance is created successfully.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        assert chat_agent is not None

    def test_initialization_create_parser(self, chat_agent):
        """Test that parser is initialized.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        assert chat_agent.parser is not None

    def test_initialization_create_prompt(self, chat_agent):
        """Test that prompt template is initialized.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        assert chat_agent.prompt is not None

    def test_initialization_create_llm(self, chat_agent):
        """Test that LLM is initialized.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        assert chat_agent.llm is not None

    def test_initialization_create_chain(self, chat_agent):
        """Test that chain is initialized.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        assert chat_agent.chain is not None

    def test_show_prompt_returns_string(self, chat_agent):
        """Test that show_prompt returns a formatted string.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        question = "What is contract law?"
        result = chat_agent.show_prompt(question)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "contract law" in result.lower()

    def test_process_empty_question_raises_error(self, chat_agent):
        """Test that process raises ValueError for empty question.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        with pytest.raises(ValueError, match="Question cannot be empty"):
            chat_agent.process("")

    def test_process_whitespace_question_raises_error(self, chat_agent):
        """Test that process raises ValueError for whitespace-only question.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        with pytest.raises(ValueError, match="Question cannot be empty"):
            chat_agent.process("   ")

    def test_process_success(self, chat_agent):
        """Test successful question processing with mocked chain.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        mock_response = ChatAgentResponse(
            answer="This is a test answer about Canadian law."
        )

        with patch.object(chat_agent, "chain") as mock_chain:
            mock_chain.invoke.return_value = mock_response

            result = chat_agent.process("What is contract law?")

            assert result is not None
            assert result.answer == "This is a test answer about Canadian law."
            mock_chain.invoke.assert_called_once_with(
                {"question": "What is contract law?"}
            )

    def test_process_logs_question(self, chat_agent, caplog):
        """Test that process method logs the question being processed.

        Args:
            chat_agent: ChatAgent instance fixture.
            caplog: Pytest fixture to capture log output.
        """
        mock_response = ChatAgentResponse(answer="Test answer")

        with caplog.at_level(logging.INFO):
            with patch.object(chat_agent, "chain") as mock_chain:
                mock_chain.invoke.return_value = mock_response

                chat_agent.process("What is contract law?")

                assert "Processing question: What is contract law" in caplog.text
                assert "Question processed successfully" in caplog.text

    def test_initialization_missing_template_raises_error(self):
        """Test that initialization fails when template files are missing."""
        with patch("agents.chat_agent.PromptTemplateLoader") as mock_loader:
            mock_loader.return_value.load_template.side_effect = FileNotFoundError(
                "Template not found"
            )

            with pytest.raises(FileNotFoundError):
                ChatAgent()
