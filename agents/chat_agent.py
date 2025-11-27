"""Chat agent module for processing user questions and returning structured responses.

This module defines a chat agent that uses LangChain and OpenAI to process user
questions about Canadian law and return structured responses.
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI

from prompt_templates.prompt_template_loader import PromptTemplateLoader
from schemas.chat_agent_schemas import ChatAgentResponse
from utils.logger import Logger

logger = Logger().get_logger()
load_dotenv()


class ChatAgent:
    """Chat agent for processing legal questions about Canadian law.

    Attributes:
        parser: Pydantic output parser for structured responses.
        prompt: Chat prompt template combining system and human messages.
        llm: ChatOpenAI language model instance.
        chain: LangChain chain combining prompt, LLM, and parser.
    """

    def __init__(self, model_name: str = "gpt-4"):
        """Initialize the chat agent with specified model.

        Args:
            model_name: Name of the OpenAI model to use. Defaults to "gpt-4".

        Raises:
            FileNotFoundError: If prompt template files cannot be found.
            ValueError: If model initialization fails.
            Exception: For other unexpected initialization errors.
        """
        try:
            # Create the parser
            logger.info("Initializing parser")
            self.parser = PydanticOutputParser(pydantic_object=ChatAgentResponse)
            format_instructions = self.parser.get_format_instructions()

            # Load the system and human templates
            logger.info("Loading prompt templates")
            ptl = PromptTemplateLoader()
            system_template = ptl.load_template("chat_agent_prompt_template_system.md")
            human_template = ptl.load_template("chat_agent_prompt_template_human.md")

            # Create the system and human messages
            system_message = SystemMessagePromptTemplate.from_template(
                template=system_template
            )
            human_message = HumanMessagePromptTemplate.from_template(
                template=human_template, input_variables=["question"]
            )

            # Combine the messages to form the prompt
            logger.info("Creating prompt template")
            self.prompt = ChatPromptTemplate.from_messages(
                [system_message, human_message]
            ).partial(format_instructions=format_instructions)

            # Define the LLM model
            logger.info(f"Initializing LLM with model: {model_name}")
            self.llm = ChatOpenAI(model=model_name)

            # Build the chain
            logger.info("Building chain")
            self.chain = self.prompt | self.llm | self.parser

            logger.info("Chat agent initialized successfully")

        except FileNotFoundError as e:
            logger.error(f"Failed to load prompt templates: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid model configuration: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during initialization: {e}")
            raise

    def show_prompt(self, question: str) -> str:
        """Display the formatted prompt for debugging purposes.

        Args:
            question: The user's question to format into the prompt.

        Returns:
            The formatted prompt as a string.

        Raises:
            Exception: If prompt formatting fails.
        """
        try:
            return self.prompt.format(question=question)
        except Exception as e:
            logger.error(f"Error formatting prompt: {e}")
            raise

    def process(self, question: str) -> ChatAgentResponse:
        """Process a user question and return a structured response.

        Args:
            question: The user's question to process.

        Returns:
            ChatAgentResponse containing the agent's answer.

        Raises:
            ValueError: If the question is empty or invalid.
            Exception: For errors during processing or parsing.
        """
        try:
            if not question or not question.strip():
                raise ValueError("Question cannot be empty")

            logger.info(f"Processing question: {question[:50]}...")
            response = self.chain.invoke({"question": question})
            logger.info("Question processed successfully")
            return response

        except ValueError as e:
            logger.error(f"Invalid question: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            raise


if __name__ == "__main__":
    try:
        chat_agent = ChatAgent()
        question = "What is the capital of Jordan?"
        response = chat_agent.process(question)
        print(f"Answer: {response.answer}")
    except Exception as e:
        logger.error(f"Failed to run chat agent: {e}")
