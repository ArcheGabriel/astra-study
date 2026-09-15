from collections.abc import Iterator

from fastapi import BackgroundTasks

from app.ai.pipeline import AIPipeline
from app.enums.message import MessageRole
from app.exceptions.chat import ChatNotFoundError
from app.models.chat import ChatSession
from app.models.message import ChatMessage
from app.models.user import User
from app.repositories.chat import ChatRepository
from app.repositories.message import MessageRepository
from app.retrieval.access import AccessContext
from app.schemas.conversation import ConversationResponse
from app.generation.models import StreamEvent
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
)
from app.services.conversation_summary import (
    ConversationSummaryService,
    run_summary_refresh,
)
from app.services.message import MessageService

from langsmith import traceable

import logging

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Orchestrates the complete AI conversation workflow.
    """

    def __init__(
        self,
        chat_repository: ChatRepository,
        message_repository: MessageRepository,
        message_service: MessageService,
        ai_pipeline: AIPipeline,
        conversation_summary_service: ConversationSummaryService,
    ):
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.message_service = message_service
        self.ai_pipeline = ai_pipeline
        self.conversation_summary_service = conversation_summary_service

    @traceable(
        name="Conversation Turn",
        run_type="chain",
    )
    def send_message(
        self,
        *,
        chat_id: int,
        current_user: User,
        access: AccessContext,
        message_data: MessageCreate,
        background_tasks: BackgroundTasks | None = None,
    ) -> ConversationResponse:
        """
        Process a complete conversation turn.

        ``current_user`` remains the authenticated-identity input for chat
        ownership and message authorship; ``access`` is the trusted
        authorization context passed downstream to retrieval.
        """

        chat = self._validate_chat(
            chat_id=chat_id,
            current_user=current_user,
        )

        user_message = self.message_service.create_message(
            chat_id=chat.id,
            current_user=current_user,
            message_data=message_data,
        )

        self._generate_chat_title_if_needed(
            chat=chat,
            first_message=message_data.content,
        )

        conversation = self.message_repository.get_conversational_messages(
            chat.id,
        )

        ai_response = self.ai_pipeline.generate_response(
            conversation=conversation,
            access=access,
            summary=chat.summary,
        )

        assistant_message = self._save_assistant_message(
            chat=chat,
            content=ai_response.answer,
        )

        # Refresh the rolling summary out of band -- it must never delay or
        # fail the user-facing response.
        self._schedule_summary_refresh(
            chat_id=chat.id,
            background_tasks=background_tasks,
        )

        return ConversationResponse(
            user_message=user_message,
            assistant_message=MessageResponse.model_validate(
                assistant_message,
            ),
            citations=ai_response.citations,
        )

    def stream_message(
        self,
        *,
        chat_id: int,
        current_user: User,
        access: AccessContext,
        message_data: MessageCreate,
        background_tasks: BackgroundTasks | None = None,
    ) -> Iterator[StreamEvent]:
        """
        Stream an AI response while persisting the final assistant message.

        ``current_user`` remains the authenticated-identity input for chat
        ownership and message authorship; ``access`` is the trusted
        authorization context passed downstream to retrieval.
        """

        chat = self._validate_chat(
            chat_id=chat_id,
            current_user=current_user,
        )

        self.message_service.create_message(
            chat_id=chat.id,
            current_user=current_user,
            message_data=message_data,
        )

        self._generate_chat_title_if_needed(
            chat=chat,
            first_message=message_data.content,
        )

        conversation = self.message_repository.get_conversational_messages(
            chat.id,
        )

        chunks: list[str] = []

        for event in self.ai_pipeline.stream_response(
            conversation=conversation,
            access=access,
            summary=chat.summary,
        ):
            if event.text is not None:
                chunks.append(event.text)
            yield event

        complete_response = "".join(chunks)

        self._save_assistant_message(
            chat=chat,
            content=complete_response,
        )

        # Refresh the rolling summary out of band. The assistant message is
        # already persisted above (so it counts towards the next boundary),
        # and this scheduling call does not block the SSE ``done`` event.
        self._schedule_summary_refresh(
            chat_id=chat.id,
            background_tasks=background_tasks,
        )

    @traceable(
        name="Validate Chat",
        run_type="chain",
    )
    def _validate_chat(
        self,
        *,
        chat_id: int,
        current_user: User,
    ) -> ChatSession:
        """
        Validate that the chat exists and belongs to the current user.
        """

        chat = self.chat_repository.get_by_id(chat_id)

        if chat is None or chat.user_id != current_user.id:
            raise ChatNotFoundError()

        return chat

    @traceable(
        name="Initialize Chat Title",
        run_type="chain",
    )
    def _generate_chat_title_if_needed(
        self,
        *,
        chat: ChatSession,
        first_message: str,
    ) -> None:
        """
        Generate an AI title for a newly created chat.
        """

        if chat.title != "New Chat":
            return

        title = self.ai_pipeline.generate_title(
            first_message=first_message,
        )

        self.chat_repository.update_title(
            chat_id=chat.id,
            title=title,
        )

    @traceable(
        name="Persist Assistant Message",
        run_type="chain",
    )
    def _save_assistant_message(
        self,
        *,
        chat: ChatSession,
        content: str,
    ) -> ChatMessage:
        """
        Persist the assistant response.
        """

        assistant_message = ChatMessage(
            chat_session_id=chat.id,
            role=MessageRole.ASSISTANT,
            content=content,
        )

        return self.message_repository.create(
            assistant_message,
        )

    def _schedule_summary_refresh(
        self,
        *,
        chat_id: int,
        background_tasks: BackgroundTasks | None,
    ) -> None:
        """
        Trigger a rolling-summary refresh without blocking the response.

        In the normal HTTP path this hands off to FastAPI ``BackgroundTasks``
        (its own DB session, runs after the response / SSE stream completes).
        When there is no background context (tests, scripts) it falls back to
        an inline refresh on the request session, still guarded so summary
        problems can never fail the turn.
        """

        if background_tasks is not None:
            background_tasks.add_task(run_summary_refresh, chat_id)
            return

        try:
            self.conversation_summary_service.update_summary(
                chat_id=chat_id,
            )
        except Exception:
            logger.exception(
                "Inline conversation summary refresh failed (chat_id=%s).",
                chat_id,
            )
