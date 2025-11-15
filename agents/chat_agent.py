"""
the class will define and agent that can process a user question and return a response
an intermediate step will be adding a show prompt function for debugging
"""

from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI

from prompt_templates.prompt_template_loader import PromptTemplateLoader

load_dotenv()


class ChatAgent:
    def __init__(self, model_name: str = "gpt-5"):
        # Define the prompt
        # load the system and human templates
        ptl = PromptTemplateLoader()
        system_template = ptl.load_template("chat_agent_prompt_template_system.md")
        human_template = ptl.load_template("chat_agent_prompt_template_human.md")

        # create the system and human messages
        system_message = SystemMessagePromptTemplate.from_template(
            template=system_template
        )
        human_message = HumanMessagePromptTemplate.from_template(
            template=human_template, input_variables=["question"]
        )

        # combine the messages to form the prompt
        self.prompt = ChatPromptTemplate.from_messages([system_message, human_message])

        # define the llm model
        self.llm = ChatOpenAI(model=model_name)

        # build the chain
        self.chain = self.prompt | self.llm

    def show_prompt(self, question: str):
        return self.prompt.format(question=question, format_instructions=None)

    def process(self, question: str):
        return self.chain


if __name__ == "__main__":
    chat_agent = ChatAgent()
    question = "What is the capital of Jordan?"
    print(chat_agent.llm.invoke(question))
