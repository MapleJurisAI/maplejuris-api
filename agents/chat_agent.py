"""
the class will define and agent that can process a user question and return a response
an intermediat step will be adding a shwo prompt function for debugging
"""
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from prompt_templates.prompt_template_loader import PromptTemplateLoader


class ChatAgent:
    def __init__(self):
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
        self.llm = None

        # build the chain
        self.chain = None

    def show_prompt(self, question: str):
        return self.prompt.format(question=question, format_instructions=None)

    def process(self, question: str):
        pass


if __name__ == "__main__":
    chat_agent = ChatAgent()
    question = "What is the capital of Jordan?"
    print(chat_agent.show_prompt(question=question))
