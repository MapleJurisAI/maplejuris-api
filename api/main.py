"""
FastAPI application entry point with OOP design.
Main application class with middleware, CORS, and lifecycle management.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import secretmanager

from api.routes import router
from utils.logger import Logger

logger = Logger().get_logger()


def get_secret(secret_name: str):
    """Fetch secret value from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.environ.get("PROJECT_ID", "maplejuris-production")
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


class MapleJurisAPI:
    """Main API application class."""

    def __init__(self):
        self.logger = Logger().get_logger()
        self.version = "1.0.0"
        self.app = self._create_app()
        self._configure_middleware()
        self._register_routes()
        # Load secrets
        self.api_key_1 = get_secret("API_KEY_1")  # Example

    def _create_app(self) -> FastAPI:
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
        self.logger.info("MapleJuris AI API starting up...")
        yield
        self.logger.info("MapleJuris AI API shutting down...")

    def _configure_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # restrict in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _register_routes(self):
        self.app.include_router(router, prefix="/api")

    def get_app(self) -> FastAPI:
        return self.app


# Create app instance
api = MapleJurisAPI()
app = api.get_app()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting development server on port {port}...")
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, log_level="info")
