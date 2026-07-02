from fastapi import APIRouter, Depends, Response, status

from app.dependencies.auth import get_current_user
from app.dependencies.services import get_chat_service
from app.models.user import User
from app.schemas.chat import (
    ChatCreate,
    ChatResponse,
    ChatUpdate,
)
from app.services.chat import ChatService

router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_chat(
    _: ChatCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """
    Create a new chat session.
    """

    chat = chat_service.create_chat(
        user_id=current_user.id,
    )

    return ChatResponse.model_validate(chat)


@router.get(
    "",
    response_model=list[ChatResponse],
)
def list_chats(
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> list[ChatResponse]:
    """
    Return all chat sessions belonging to the current user.
    """

    chats = chat_service.list_chats(
        user_id=current_user.id,
    )

    return [
        ChatResponse.model_validate(chat)
        for chat in chats
    ]


@router.get(
    "/{chat_id}",
    response_model=ChatResponse,
)
def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """
    Return a chat session.
    """

    chat = chat_service.get_chat(
        chat_id=chat_id,
        user_id=current_user.id,
    )

    return ChatResponse.model_validate(chat)


@router.patch(
    "/{chat_id}",
    response_model=ChatResponse,
)
def rename_chat(
    chat_id: int,
    chat_update: ChatUpdate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """
    Rename a chat session.
    """

    chat = chat_service.rename_chat(
        chat_id=chat_id,
        user_id=current_user.id,
        title=chat_update.title,
    )

    return ChatResponse.model_validate(chat)


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> Response:
    """
    Delete a chat session.
    """

    chat_service.delete_chat(
        chat_id=chat_id,
        user_id=current_user.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )