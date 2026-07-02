from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatCreate(BaseModel):
    """
    Request schema for creating a chat session.

    Currently empty because the backend initializes
    the chat with default values.
    """

    model_config = ConfigDict(
        extra="forbid",
    )


class ChatUpdate(BaseModel):
    """
    Request schema for renaming a chat session.
    """

    title: str = Field(
        min_length=1,
        max_length=255,
    )


class ChatResponse(BaseModel):
    """
    Response schema for a chat session.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    title: str
    user_id: int
    created_at: datetime
    updated_at: datetime