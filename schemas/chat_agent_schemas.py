from pydantic import BaseModel, Field


class ChatAgentResponse(BaseModel):
    """Response model for chat agent output.

    Attributes:
        answer: The agent's text response to the user's question.
    """

    answer: str = Field(
        ..., description="The agent's text response to the user's question"
    )
