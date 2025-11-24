"""Schema for ChatGraph state management.

This module defines the state structure used by the ChatGraph to manage
conversation flow and error handling.
"""

from pydantic import BaseModel, Field


class ChatGraphState(BaseModel):
    """State model for managing chat graph execution.

    This class defines the state structure passed between nodes in the chat graph,
    tracking the user's question, the agent's answer, and any errors that occur
    during processing.

    Attributes:
        question: The user's input question.
        answer: The agent's response to the question.
        error: Any error message encountered during graph execution.
    """

    question: str = Field(..., description="The user's input question")
    answer: str | None = Field(
        default="", description="The agent's response to the question"
    )
    error: str | None = Field(
        default="", description="Error message if processing fails"
    )
