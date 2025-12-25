"""Schema for ChatGraph state management.

This module defines the state structure used by the ChatGraph to manage
conversation flow and error handling.
"""

from pydantic import BaseModel, Field


class ChatGraphState(BaseModel):
    """State model for managing chat graph execution.

    This class defines the state structure passed between nodes in the chat graph,
    tracking the user's question, the agent's answer, retrieved sections, and any errors.

    Attributes:
        question: The user's input question.
        needs_retrieval: Whether the question requires retrieval from legal sections.
        retrieved_sections: List of retrieved sections with their metadata.
        answer: The agent's response to the question.
        error: Any error message encountered during graph execution.
    """

    question: str = Field(..., description="The user's input question")
    needs_retrieval: bool = Field(
        default=False, description="Whether retrieval is needed"
    )
    retrieved_sections: list[dict] = Field(
        default_factory=list,
        description="Retrieved sections from similarity search",
    )
    answer: str | None = Field(
        default="", description="The agent's response to the question"
    )
    error: str | None = Field(
        default="", description="Error message if processing fails"
    )
