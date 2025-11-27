"""API route handlers with OOP design.

Defines all API endpoints using dependency injection and class-based design.
"""

from fastapi import HTTPException, status
from fastapi.routing import APIRouter as FastAPIRouter

from graphs.chat_graph import ChatGraph
from schemas.api_schemas import ChatResponse, HealthResponse, QuestionRequest
from utils.logger import Logger


class ChatService:
    """Service class for chat operations."""

    def __init__(self):
        """Initialize chat service with graph."""
        self.logger = Logger().get_logger()
        self.chat_graph = ChatGraph()
        self.logger.info("ChatService initialized")

    def process_question(self, question: str) -> ChatResponse:
        """Process a question through the chat graph.

        Args:
            question: User's question

        Returns:
            ChatResponse with answer or error

        Raises:
            Exception: If processing fails
        """
        try:
            self.logger.info(f"Processing question: {question[:50]}...")
            result = self.chat_graph.run(question=question)

            if result.error:
                self.logger.warning(f"Graph returned error: {result.error}")

            return ChatResponse(
                question=result.question, answer=result.answer, error=result.error
            )

        except Exception as e:
            self.logger.error(f"Error in ChatService: {e}")
            raise


class HealthService:
    """Service class for health check operations."""

    def __init__(self):
        """Initialize health service."""
        self.logger = Logger().get_logger()
        self.version = "1.0.0"

    def check_health(self) -> HealthResponse:
        """Check service health.

        Returns:
            HealthResponse with status
        """
        self.logger.debug("Health check performed")
        return HealthResponse(status="healthy", version=self.version)


class RouteManager:
    """Main API router with dependency injection."""

    def __init__(self):
        """Initialize router with services."""
        self.router = FastAPIRouter()
        self.chat_service = ChatService()
        self.health_service = HealthService()
        self.logger = Logger().get_logger()
        self._register_routes()

    def _register_routes(self):
        """Register all routes."""
        self.router.add_api_route(
            "/health",
            self.health_check,
            methods=["GET"],
            response_model=HealthResponse,
            tags=["Health"],
        )

        self.router.add_api_route(
            "/chat",
            self.chat,
            methods=["POST"],
            response_model=ChatResponse,
            status_code=status.HTTP_200_OK,
            tags=["Chat"],
            summary="Process a legal question",
            description="Submit a question about Canadian law and receive an AI-generated answer.",
        )

    async def health_check(self) -> HealthResponse:
        """Health check endpoint.

        Returns:
            HealthResponse with service status
        """
        return self.health_service.check_health()

    async def chat(self, request: QuestionRequest) -> ChatResponse:
        """Process a chat question through the graph.

        Args:
            request: Question from user

        Returns:
            ChatResponse with answer or error

        Raises:
            HTTPException: If processing fails critically
        """
        try:
            return self.chat_service.process_question(question=request.question)

        except Exception as e:
            self.logger.error(f"Critical error in chat endpoint: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process question. Please try again.",
            )

    def get_router(self) -> FastAPIRouter:
        """Get the configured router.

        Returns:
            Configured FastAPI router
        """
        return self.router


# Create router instance
route_manager = RouteManager()
router = route_manager.get_router()
