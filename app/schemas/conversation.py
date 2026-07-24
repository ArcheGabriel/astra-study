from pydantic import BaseModel, ConfigDict, Field

from app.generation.models import Citation
from app.schemas.message import MessageResponse


class ConversationResponse(BaseModel):
    """
    Response returned after sending a message.

    Contains both the persisted user message,
    the generated assistant response and the
    citations supporting the generated answer.
    """

    user_message: MessageResponse

    assistant_message: MessageResponse

    citations: list[Citation] = Field(
        default_factory=list,
        description="Document citations supporting the assistant response.",
    )

    model_config = ConfigDict(
        from_attributes=True,
    )