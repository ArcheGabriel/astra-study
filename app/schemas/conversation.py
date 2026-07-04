from pydantic import BaseModel, ConfigDict

from app.schemas.message import MessageResponse


class ConversationResponse(BaseModel):
    """
    Response returned after sending a message.

    Contains both the user's message and
    the assistant's generated response.
    """

    user_message: MessageResponse

    assistant_message: MessageResponse

    model_config = ConfigDict(
        from_attributes=True,
    )