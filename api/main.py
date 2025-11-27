"""FastAPI application entry point with OOP design.

Main application class with middleware, CORS, and lifecycle management.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from utils.logger import Logger

logger = Logger().get_logger()


class MapleJurisAPI:
    """Main API application class."""

    def __init__(self):
        """Initialize API application."""
        self.logger = Logger().get_logger()
        self.version = "1.0.0"
        self.app = self._create_app()
        self._configure_middleware()
        self._register_routes()

    def _create_app(self) -> FastAPI:
        """Create FastAPI application instance.

        Returns:
            Configured FastAPI app
        """
        return FastAPI(
            title="MapleJuris AI API",
            description="AI-powered Canadian legal research assistant",
            version=self.version,
            docs_url="/docs",
            redoc_url="/redoc",
            lifespan=self._lifespan,
        )

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """Manage application lifecycle.

        Args:
            app: FastAPI application instance
        """
        # Startup
        self.logger.info("MapleJuris AI API starting up...")
        self.logger.info("Documentation available at /docs")
        yield
        # Shutdown
        self.logger.info("MapleJuris AI API shutting down...")

    def _configure_middleware(self):
        """Configure application middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Update with specific origins in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _register_routes(self):
        """Register API routes."""
        self.app.include_router(router, prefix="/api")

    def get_app(self) -> FastAPI:
        """Get the FastAPI application.

        Returns:
            Configured FastAPI app
        """
        return self.app


# Create application instance
api = MapleJurisAPI()
app = api.get_app()


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
