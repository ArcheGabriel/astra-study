from fastapi import APIRouter, Depends, status

from app.dependencies.auth import get_current_user
from app.dependencies.services import (
    get_conversation_service,
    get_message_service,
)
from app.models.user import User
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
)
from app.services.conversation import ConversationService
from app.services.message import MessageService

router = APIRouter(
    prefix="/chats/{chat_id}/messages",
    tags=["Messages"],
)


@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(
        get_conversation_service,
    ),
) -> MessageResponse:
    """
    Send a message and generate an AI response.
    """

    return conversation_service.send_message(
        chat_id=chat_id,
        current_user=current_user,
        message_data=message_data,
    )


@router.get(
    "",
    response_model=list[MessageResponse],
    status_code=status.HTTP_200_OK,
)
def get_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(
        get_message_service,
    ),
) -> list[MessageResponse]:
    """
    Retrieve all messages for a chat session.
    """

    return message_service.get_messages(
        chat_id=chat_id,
        current_user=current_user,
    )