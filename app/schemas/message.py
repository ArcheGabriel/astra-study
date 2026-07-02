from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums.message import MessageRole


class MessageCreate(BaseModel):
    """
    Request schema for sending a user message.
    """

    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Message content sent by the user.",
        examples=[
            "Explain semantic chunking.",
        ],
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class MessageResponse(BaseModel):
    """
    Response schema representing a chat message.
    """

    id: int

    role: MessageRole

    content: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )