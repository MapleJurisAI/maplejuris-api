"""Chat graph module for orchestrating conversational AI workflows.

This module implements a LangGraph-based workflow for processing user questions
through a chat agent with error handling capabilities.
"""

from langgraph.graph import END, START, StateGraph

from agents.chat_agent import ChatAgent
from schemas.chat_graph_schemas import ChatGraphState
from utils.logger import Logger

logger = Logger().get_logger()


class ChatGraph:
    """Orchestrates chat workflows using LangGraph.

    This class manages a graph-based workflow that processes user questions
    through a chat agent, with built-in error handling and conditional routing.

    Attributes:
        chat_agent: Instance of ChatAgent for processing questions.
        graph: Compiled LangGraph workflow.
    """

    def __init__(self):
        """Initialize the chat graph with agents and workflow."""
        logger.info("Initializing ChatGraph")

        # Initialize the agents
        logger.info("Creating chat agent")
        self.chat_agent = ChatAgent()

        # Create the graph
        logger.info("Building graph workflow")
        self.graph = self._build_graph()

        logger.info("ChatGraph initialized successfully")

    def _build_graph(self) -> StateGraph:
        """Build and compile the LangGraph workflow.

        Creates a graph with nodes for processing chat and handling errors,
        with conditional routing based on success/failure.

        Returns:
            Compiled LangGraph workflow.
        """
        logger.info("Creating StateGraph workflow")
        workflow = StateGraph(ChatGraphState)

        # Add nodes
        logger.info("Adding graph nodes")
        workflow.add_node("process_chat_agent_node", self.process_chat_agent_node)
        workflow.add_node("_handle_error", self._handle_error)

        # Add edges
        logger.info("Adding graph edges")
        workflow.add_edge(START, "process_chat_agent_node")
        workflow.add_conditional_edges(
            "process_chat_agent_node",
            self._process_chat_agent_node_router,
            {"pass": END, "fail": "_handle_error"},
        )
        workflow.add_edge("_handle_error", END)

        logger.info("Compiling graph")
        return workflow.compile()

    def _handle_error(self, state: ChatGraphState) -> ChatGraphState:
        """Handle errors that occur during graph execution.

        Args:
            state: Current graph state.

        Returns:
            Updated state with error message.
        """
        logger.error(f"Error handling triggered for question: {state.question}")
        return ChatGraphState(
            question=state.question, answer=None, error="Error executing the graph"
        )

    def process_chat_agent_node(self, state: ChatGraphState) -> ChatGraphState:
        """Process user question through the chat agent.

        Args:
            state: Current graph state containing the user question.

        Returns:
            Updated state with agent's answer.

        Raises:
            Exception: If agent processing fails.
        """
        try:
            question = state.question
            logger.info(f"Processing question in chat agent node: {question[:50]}...")

            response = self.chat_agent.process(question=question)

            logger.info("Chat agent processing completed successfully")
            return ChatGraphState(
                question=state.question, answer=response.answer, error=None
            )
        except Exception as e:
            logger.error(f"Error in chat agent node: {e}")
            return ChatGraphState(question=state.question, answer=None, error=str(e))

    def _process_chat_agent_node_router(self, state: ChatGraphState) -> str:
        """Route graph flow based on chat agent node success.

        Args:
            state: Current graph state.

        Returns:
            "pass" if answer exists, "fail" otherwise.
        """
        route = "pass" if state.answer else "fail"
        logger.info(f"Routing to: {route}")
        return route

    def run(self, question: str) -> ChatGraphState:
        """Run the chat graph with a user question.

        Args:
            question: The user's input question.

        Returns:
            The final state as a ChatGraphState object.

        Raises:
            Exception: If graph execution fails.
        """
        try:
            logger.info(f"Running chat graph for question: {question[:50]}...")

            initial_state = ChatGraphState(question=question, answer=None, error=None)

            final_state_dict = self.graph.invoke(initial_state)
            final_state = ChatGraphState(**final_state_dict)

            logger.info("Chat graph execution completed")
            return final_state

        except Exception as e:
            logger.error(f"Error running chat graph: {e}")
            raise


if __name__ == "__main__":
    try:
        logger.info("Starting chat graph demo")
        chat_graph = ChatGraph()
        question = "What is the capital of Canada?"

        result = chat_graph.run(question=question)

        print(f"\nQuestion: {result.question}")
        print(f"Answer: {result.answer}")
        if result.error:
            print(f"Error: {result.error}")

    except Exception as e:
        logger.error(f"Failed to run chat graph demo: {e}")
