"""API request and response models.

Pydantic models for API input validation and response serialization.
"""

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """Request model for chat questions."""

    question: str = Field(..., min_length=1, description="User's question")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the requirements for incorporating in Ontario?"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat answers."""

    question: str = Field(..., description="Original question")
    answer: str | None = Field(None, description="AI-generated answer")
    error: str | None = Field(None, description="Error message if any")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the requirements for incorporating in Ontario?",
                "answer": "To incorporate in Ontario, you need...",
                "error": None,
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")

    class Config:
        json_schema_extra = {"example": {"status": "healthy", "version": "1.0.0"}}
