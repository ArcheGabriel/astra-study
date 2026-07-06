from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.pipeline import AIPipeline
from app.database.session import get_db
from app.repositories.chat import ChatRepository
from app.repositories.message import MessageRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.chat import ChatService
from app.services.conversation import ConversationService
from app.services.llm import LLMService
from app.services.message import MessageService
from app.services.user import UserService
from app.repositories.document import DocumentRepository
from app.services.document import DocumentService
from app.storage.local import LocalStorageService


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


def get_llm_service() -> LLMService:
    """
    Dependency for LLMService.
    """

    return LLMService()


def get_ai_pipeline(
    llm_service: Annotated[
        LLMService,
        Depends(get_llm_service),
    ],
) -> AIPipeline:
    """
    Dependency for AIPipeline.
    """

    return AIPipeline(
        llm_service=llm_service,
    )


def get_conversation_service(
    db: Annotated[Session, Depends(get_db)],
    message_service: Annotated[
        MessageService,
        Depends(get_message_service),
    ],
    ai_pipeline: Annotated[
        AIPipeline,
        Depends(get_ai_pipeline),
    ],
) -> ConversationService:
    """
    Dependency for ConversationService.
    """

    chat_repository = ChatRepository(db)
    message_repository = MessageRepository(db)

    return ConversationService(
        chat_repository=chat_repository,
        message_repository=message_repository,
        message_service=message_service,
        ai_pipeline=ai_pipeline,
    )


def get_document_service(
    db: Annotated[Session, Depends(get_db)],
) -> DocumentService:
    """
    Dependency for DocumentService.
    """

    document_repository = DocumentRepository(
        db,
    )

    storage_service = LocalStorageService()

    return DocumentService(
        document_repository=document_repository,
        storage_service=storage_service,
    )