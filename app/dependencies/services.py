from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.pipeline import AIPipeline
from app.database.session import get_db

from app.repositories.chat import ChatRepository
from app.repositories.document import DocumentRepository
from app.repositories.message import MessageRepository
from app.repositories.user import UserRepository

from app.services.auth import AuthService
from app.services.chat import ChatService
from app.services.conversation import ConversationService
from app.services.document import DocumentService
from app.services.ingestion import IngestionService
from app.services.llm import LLMService
from app.services.message import MessageService
from app.services.user import UserService

from app.storage.local import LocalStorageService

from app.generation.prompt_builder import PromptBuilder
from app.generation.service import GenerationService

from app.search.hybrid.service import HybridService
from app.reranking.service import RerankingService
from app.retrieval.service import RetrievalService
from app.services.conversation_summary import ConversationSummaryService
from app.dependencies.resources import get_llm_resource
from app.dependencies.resources import get_reranking_resource


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
) -> UserService:

    user_repository = UserRepository(db)

    return UserService(
        user_repository=user_repository,
    )


def get_auth_service(
    db: Annotated[Session, Depends(get_db)],
) -> AuthService:

    user_repository = UserRepository(db)

    return AuthService(
        user_repository=user_repository,
    )


def get_chat_service(
    db: Annotated[Session, Depends(get_db)],
) -> ChatService:

    chat_repository = ChatRepository(db)

    return ChatService(
        chat_repository=chat_repository,
    )


def get_message_service(
    db: Annotated[Session, Depends(get_db)],
) -> MessageService:

    chat_repository = ChatRepository(db)
    message_repository = MessageRepository(db)

    return MessageService(
        chat_repository=chat_repository,
        message_repository=message_repository,
    )


# ----------------------------------------------------------------------
# LLM
# ----------------------------------------------------------------------

def get_llm_service() -> LLMService:

    return get_llm_resource()


# ----------------------------------------------------------------------
# Prompt Builder
# ----------------------------------------------------------------------

def get_prompt_builder() -> PromptBuilder:

    return PromptBuilder()


# ----------------------------------------------------------------------
# Hybrid Search
# ----------------------------------------------------------------------

def get_hybrid_service() -> HybridService:

    return HybridService()


# ----------------------------------------------------------------------
# Reranker
# ----------------------------------------------------------------------

def get_reranking_service() -> RerankingService:

    return get_reranking_resource()


# ----------------------------------------------------------------------
# Retrieval
# ----------------------------------------------------------------------

def get_retrieval_service(
    hybrid_service: Annotated[
        HybridService,
        Depends(get_hybrid_service),
    ],
    reranking_service: Annotated[
        RerankingService,
        Depends(get_reranking_service),
    ],
) -> RetrievalService:

    return RetrievalService(
        hybrid_service=hybrid_service,
        reranking_service=reranking_service,
    )


# ----------------------------------------------------------------------
# Generation
# ----------------------------------------------------------------------

def get_generation_service(
    prompt_builder: Annotated[
        PromptBuilder,
        Depends(get_prompt_builder),
    ],
    llm_service: Annotated[
        LLMService,
        Depends(get_llm_service),
    ],
) -> GenerationService:

    return GenerationService(
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )


# ----------------------------------------------------------------------
# AI Pipeline
# ----------------------------------------------------------------------

def get_ai_pipeline(
    retrieval_service: Annotated[
        RetrievalService,
        Depends(get_retrieval_service),
    ],
    generation_service: Annotated[
        GenerationService,
        Depends(get_generation_service),
    ],
    llm_service: Annotated[
        LLMService,
        Depends(get_llm_service),
    ],
) -> AIPipeline:
    """
    Dependency for AIPipeline.
    """

    return AIPipeline(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        llm_service=llm_service,
    )

# ----------------------------------------------------------------------
# Conversation Summary
# ----------------------------------------------------------------------

def get_conversation_summary_service(
    db: Annotated[Session, Depends(get_db)],
    ai_pipeline: Annotated[
        AIPipeline,
        Depends(get_ai_pipeline),
    ],
) -> ConversationSummaryService:

    chat_repository = ChatRepository(db)
    message_repository = MessageRepository(db)

    return ConversationSummaryService(
        chat_repository=chat_repository,
        message_repository=message_repository,
        ai_pipeline=ai_pipeline,
    )


# ----------------------------------------------------------------------
# Conversation
# ----------------------------------------------------------------------

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
    conversation_summary_service: Annotated[
        ConversationSummaryService,
        Depends(get_conversation_summary_service),
    ],
) -> ConversationService:

    chat_repository = ChatRepository(db)
    message_repository = MessageRepository(db)

    return ConversationService(
        chat_repository=chat_repository,
        message_repository=message_repository,
        message_service=message_service,
        ai_pipeline=ai_pipeline,
        conversation_summary_service=conversation_summary_service,
    )

# ----------------------------------------------------------------------
# Document
# ----------------------------------------------------------------------

def get_document_service(
    db: Annotated[Session, Depends(get_db)],
) -> DocumentService:

    document_repository = DocumentRepository(db)

    storage_service = LocalStorageService()

    return DocumentService(
        document_repository=document_repository,
        storage_service=storage_service,
    )


# ----------------------------------------------------------------------
# Ingestion
# ----------------------------------------------------------------------

def get_ingestion_service(
    db: Annotated[Session, Depends(get_db)],
) -> IngestionService:

    document_repository = DocumentRepository(db)

    storage_service = LocalStorageService()

    return IngestionService(
        document_repository=document_repository,
        storage_service=storage_service,
    )