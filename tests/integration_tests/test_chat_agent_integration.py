"""Integration tests for ChatAgent with real LLM calls."""

import pytest

from agents.chat_agent import ChatAgent
from schemas.chat_agent_schemas import ChatAgentResponse


@pytest.mark.integration
class TestChatAgentIntegration:
    """Integration test suite for ChatAgent with real API calls."""

    @pytest.fixture
    def chat_agent(self):
        """Fixture to create a ChatAgent instance.

        Returns:
            ChatAgent: An instance of the chat agent.
        """
        return ChatAgent(model_name="gpt-4")

    def test_process_with_real_llm(self, chat_agent):
        """Test processing a question with real OpenAI API call.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        question = "What is contract law in Canada?"
        result = chat_agent.process(question)

        # Verify response structure
        assert result is not None
        assert hasattr(result, "answer")
        assert result.answer is not None

        # Verify response content quality
        assert len(result.answer) > 50  # Should be a substantial answer
        assert isinstance(result.answer, str)

        # Verify it's about the topic
        assert any(
            keyword in result.answer.lower()
            for keyword in ["contract", "agreement", "law", "canada"]
        )

    def test_process_multiple_questions(self, chat_agent):
        """Test processing multiple questions in sequence.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        questions = [
            "What is tort law?",
            "Explain negligence in Canadian law.",
            "What is the difference between civil and criminal law?",
        ]

        for question in questions:
            result = chat_agent.process(question)

            assert result is not None
            assert result.answer is not None
            assert len(result.answer) > 30
            assert isinstance(result.answer, str)

    def test_response_follows_format_instructions(self, chat_agent):
        """Test that responses follow the Pydantic schema format.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        question = "What is criminal law?"
        result = chat_agent.process(question)

        # Verify it returns correct type
        assert isinstance(result, ChatAgentResponse)

        # Verify all required fields are present
        assert hasattr(result, "answer")
        assert result.answer is not None

    def test_handles_complex_legal_question(self, chat_agent):
        """Test handling of complex multi-part legal question.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        question = (
            "What are the key elements required to establish a valid contract "
            "under Canadian law, and what remedies are available for breach of contract?"
        )
        result = chat_agent.process(question)

        assert result is not None
        assert len(result.answer) > 100  # Complex question should have detailed answer

        # Check for relevant concepts
        relevant_keywords = ["contract", "elements", "breach", "remedy", "remedies"]
        assert any(keyword in result.answer.lower() for keyword in relevant_keywords)

    def test_cites_canadian_legislation(self, chat_agent):
        """Test that responses cite Canadian legislation when applicable.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        question = "What legislation governs consumer protection in Canada?"
        result = chat_agent.process(question)

        assert result is not None
        assert len(result.answer) > 50

        # Should mention legislation or acts
        legal_terms = ["act", "legislation", "statute", "law", "code"]
        assert any(term in result.answer.lower() for term in legal_terms)

    def test_uses_plain_english(self, chat_agent):
        """Test that responses use plain English as instructed.

        Args:
            chat_agent: ChatAgent instance fixture.
        """
        question = "What is defamation?"
        result = chat_agent.process(question)

        assert result is not None
        # Response should be clear and not overly technical
        # This is subjective but we check for basic clarity
        assert len(result.answer.split(".")) >= 2  # At least 2 sentences
        assert result.answer[0].isupper()  # Starts with capital letter
