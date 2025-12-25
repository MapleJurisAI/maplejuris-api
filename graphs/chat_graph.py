"""Chat graph module for orchestrating conversational AI workflows.

This module implements a LangGraph-based workflow for processing user questions
through a chat agent with error handling capabilities.
"""

from typing import Optional

from langgraph.graph import END, START, StateGraph

from agents.chat_agent import ChatAgent
from agents.retrieval_agent import RetrievalAgent
from schemas.chat_graph_schemas import ChatGraphState
from utils.logger import Logger

logger = Logger().get_logger()


class ChatGraph:
    """Orchestrates chat workflows using LangGraph.

    This class manages a graph-based workflow that processes user questions
    through a chat agent, with built-in error handling and conditional routing.

    Attributes:
        chat_agent: Instance of ChatAgent for processing questions.
        retrieval_agent: Optional RetrievalAgent instance for semantic search.
        graph: Compiled LangGraph workflow.
    """

    def __init__(self, retrieval_agent: Optional[RetrievalAgent] = None):
        """Initialize the chat graph with agents and workflow.

        Args:
            retrieval_agent: Optional RetrievalAgent instance. If None, will be created.
        """
        logger.info("Initializing ChatGraph")

        # Initialize the agents
        logger.info("Creating chat agent")
        self.chat_agent = ChatAgent()

        # Initialize retrieval agent if not provided
        self.retrieval_agent: Optional[RetrievalAgent] = retrieval_agent
        if not retrieval_agent:
            logger.info("Retrieval agent not provided, will be created when needed")

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
        workflow.add_node("route_question", self.route_question_node)
        workflow.add_node("retrieve_sections", self.retrieve_sections_node)
        workflow.add_node("process_chat_agent_node", self.process_chat_agent_node)
        workflow.add_node("_handle_error", self._handle_error)

        # Add edges
        logger.info("Adding graph edges")
        workflow.add_edge(START, "route_question")
        workflow.add_conditional_edges(
            "route_question",
            self._route_question_router,
            {
                "retrieve": "retrieve_sections",
                "direct_answer": "process_chat_agent_node",
            },
        )
        workflow.add_edge("retrieve_sections", "process_chat_agent_node")
        workflow.add_conditional_edges(
            "process_chat_agent_node",
            self._process_chat_agent_node_router,
            {"pass": END, "fail": "_handle_error"},
        )
        workflow.add_edge("_handle_error", END)

        logger.info("Compiling graph")
        return workflow.compile()

    def route_question_node(self, state: ChatGraphState) -> ChatGraphState:
        """Route question to determine if retrieval is needed.

        Simple heuristic: if question contains legal keywords or asks about laws/acts,
        route to retrieval. Otherwise, answer directly.

        Args:
            state: Current graph state.

        Returns:
            Updated state with needs_retrieval flag set.
        """
        question_lower = state.question.lower()

        # Keywords that suggest need for legal retrieval
        legal_keywords = [
            "law",
            "legal",
            "act",
            "statute",
            "section",
            "penalty",
            "offence",
            "crime",
            "criminal",
            "regulation",
            "canada",
            "canadian",
            "legislation",
        ]

        needs_retrieval = any(keyword in question_lower for keyword in legal_keywords)

        logger.info(f"Routing decision: needs_retrieval={needs_retrieval}")

        return ChatGraphState(
            question=state.question,
            needs_retrieval=needs_retrieval,
            retrieved_sections=[],
            answer=None,
            error=None,
        )

    def _route_question_router(self, state: ChatGraphState) -> str:
        """Route based on whether retrieval is needed.

        Args:
            state: Current graph state.

        Returns:
            "retrieve" if retrieval needed, "direct_answer" otherwise.
        """
        route = "retrieve" if state.needs_retrieval else "direct_answer"
        logger.info(f"Routing to: {route}")
        return route

    def retrieve_sections_node(self, state: ChatGraphState) -> ChatGraphState:
        """Retrieve relevant sections using the retrieval agent.

        Args:
            state: Current graph state.

        Returns:
            Updated state with retrieved_sections populated.
        """
        try:
            if not self.retrieval_agent:
                # Initialize with default connection string (from env)
                import os

                from dotenv import load_dotenv

                load_dotenv()
                db_host = os.getenv("SQL_HOST", "localhost")
                db_port = os.getenv("SQL_PORT", "5432")
                db_name = os.getenv("SQL_DATABASE", "maplejuris")
                db_user = os.getenv("SQL_USER", "")
                db_password = os.getenv("SQL_PASSWORD", "")

                if not db_user:
                    connection_string = f"postgresql:///{db_name}"
                elif db_password:
                    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                else:
                    connection_string = (
                        f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
                    )

                self.retrieval_agent = RetrievalAgent(
                    connection_string=connection_string
                )

            logger.info(f"Retrieving sections for: {state.question[:50]}...")
            retrieved = self.retrieval_agent.process(state.question, k=5)

            logger.info(f"Retrieved {len(retrieved)} sections")
            return ChatGraphState(
                question=state.question,
                needs_retrieval=True,
                retrieved_sections=retrieved,
                answer=None,
                error=None,
            )
        except Exception as e:
            logger.error(f"Error in retrieval node: {e}")
            return ChatGraphState(
                question=state.question,
                needs_retrieval=True,
                retrieved_sections=[],
                answer=None,
                error=str(e),
            )

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

        If retrieved_sections exist, they will be included in the context.
        If not, the question is answered directly.

        Args:
            state: Current graph state containing the user question and optionally retrieved sections.

        Returns:
            Updated state with agent's answer.

        Raises:
            Exception: If agent processing fails.
        """
        try:
            question = state.question
            logger.info(f"Processing question in chat agent node: {question[:50]}...")

            # If we have retrieved sections, format them as context
            if state.retrieved_sections:
                context = "\n\nRelevant legal sections:\n"
                for i, section in enumerate(state.retrieved_sections, 1):
                    context += f"\n{i}. {section.get('statute_title', 'Unknown')} - Section {section.get('label', 'N/A')}\n"
                    context += f"   {section.get('text', '')[:300]}...\n"

                # Append context to question for the chat agent
                enhanced_question = f"{question}\n\n{context}"
                logger.info("Including retrieved sections in context")
            else:
                enhanced_question = question

            response = self.chat_agent.process(question=enhanced_question)

            logger.info("Chat agent processing completed successfully")
            return ChatGraphState(
                question=state.question,
                needs_retrieval=state.needs_retrieval,
                retrieved_sections=state.retrieved_sections,
                answer=response.answer,
                error=None,
            )
        except Exception as e:
            logger.error(f"Error in chat agent node: {e}")
            return ChatGraphState(
                question=state.question,
                needs_retrieval=state.needs_retrieval,
                retrieved_sections=state.retrieved_sections,
                answer=None,
                error=str(e),
            )

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

            initial_state = ChatGraphState(
                question=question,
                needs_retrieval=False,
                retrieved_sections=[],
                answer=None,
                error=None,
            )

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

        print("\n" + "=" * 50)
        print("Chat Graph Demo - Ask questions about Canadian law")
        print("Type 'exit', 'quit', or 'q' to stop")
        print("=" * 50 + "\n")

        while True:
            # Get user input
            question = input("\nYour question: ").strip()

            # Check for exit commands
            if question.lower() in ["exit", "quit", "q", ""]:
                print("\nExiting chat graph demo. Goodbye!")
                break

            # Process question
            try:
                result = chat_graph.run(question=question)

                print(f"\n{'─'*50}")
                print(f"Answer: {result.answer}")
                if result.error:
                    print(f"Error: {result.error}")
                print(f"{'─'*50}")

            except Exception as e:
                logger.error(f"Error processing question: {e}")
                print(f"\n❌ Error: {e}")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        logger.error(f"Failed to run chat graph demo: {e}")
