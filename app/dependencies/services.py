from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.chat import ChatRepository
from app.repositories.message import MessageRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.chat import ChatService
from app.services.message import MessageService
from app.services.user import UserService


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
) -> UserService:
    """
    Dependency for UserService.
    """

    user_repository = UserRepository(db)

    return UserService(
        user_repository=user_repository,
    )


def get_auth_service(
    db: Annotated[Session, Depends(get_db)],
) -> AuthService:
    """
    Dependency for AuthService.
    """

    user_repository = UserRepository(db)

    return AuthService(
        user_repository=user_repository,
    )


def get_chat_service(
    db: Annotated[Session, Depends(get_db)],
) -> ChatService:
    """
    Dependency for ChatService.
    """

    chat_repository = ChatRepository(db)

    return ChatService(
        chat_repository=chat_repository,
    )


def get_message_service(
    db: Annotated[Session, Depends(get_db)],
) -> MessageService:
    """
    Dependency for MessageService.
    """

    chat_repository = ChatRepository(db)
    message_repository = MessageRepository(db)

    return MessageService(
        chat_repository=chat_repository,
        message_repository=message_repository,
    )