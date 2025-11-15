import pytest

from agents.chat_agent import ChatAgent


class TestChatAgent:
    @pytest.fixture
    def chat_agent(self):
        return ChatAgent(model_name="gpt-4")

    def test_initialization_success(self, chat_agent):
        assert chat_agent is not None

    def test_initialization_create_parser(self, chat_agent):
        assert chat_agent.parser is not None

    def test_initialization_create_prompt(self, chat_agent):
        assert chat_agent.prompt is not None

    def test_initialization_create_llm(self, chat_agent):
        assert chat_agent.llm is not None

    def test_initialization_create_chain(self, chat_agent):
        assert chat_agent.chain is not None
