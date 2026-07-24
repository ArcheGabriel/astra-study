from app.schemas.conversation import ConversationResponse
from app.ai.pipeline import AIPipeline
from app.enums.message import MessageRole
from app.exceptions.chat import ChatNotFoundError
from app.models.chat import ChatSession
from app.models.message import ChatMessage
from app.models.user import User
from app.repositories.chat import ChatRepository
from app.repositories.message import MessageRepository
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
)
from app.services.message import MessageService
from collections.abc import Iterator
from app.schemas.conversation import ConversationResponse


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
    ):
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.message_service = message_service
        self.ai_pipeline = ai_pipeline

    def send_message(
        self,
        *,
        chat_id: int,
        current_user: User,
        message_data: MessageCreate,
    ) -> ConversationResponse:
        """
        Process a complete conversation turn.
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

        conversation = self.message_repository.get_by_chat_session(
            chat.id,
        )

        ai_response = self.ai_pipeline.generate_response(
            conversation=conversation,
            user_id=current_user.id,
        )

        assistant_message = self._save_assistant_message(
            chat=chat,
            content=ai_response.answer,
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
        message_data: MessageCreate,
    ) -> Iterator[str]:
        """
        Stream an AI response while persisting the final assistant message.
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

        conversation = self.message_repository.get_by_chat_session(
            chat.id,
        )

        chunks: list[str] = []

        for chunk in self.ai_pipeline.stream_response(
            conversation=conversation,
            user_id=current_user.id,
        ):
            chunks.append(chunk)
            yield chunk

        complete_response = "".join(chunks)

        self._save_assistant_message(
            chat=chat,
            content=complete_response,
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