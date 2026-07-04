from app.ai.pipeline import AIPipeline
from app.enums.message import MessageRole
from app.exceptions.chat import ChatNotFoundError
from app.models.message import ChatMessage
from app.models.user import User
from app.repositories.chat import ChatRepository
from app.repositories.message import MessageRepository
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
)
from app.services.message import MessageService


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
    ) -> MessageResponse:
        """
        Process a complete conversation turn.
        """

        chat = self.chat_repository.get_by_id(
            chat_id,
        )

        if chat is None or chat.user_id != current_user.id:
            raise ChatNotFoundError()

        user_message = self.message_service.create_message(
            chat_id=chat_id,
            current_user=current_user,
            message_data=message_data,
        )

        conversation = self.message_repository.get_by_chat_session(
            chat_id,
        )

        assistant_response = self.ai_pipeline.generate_response(
            conversation=conversation,
            user_message=message_data.content,
        )

        assistant_message = ChatMessage(
            chat_session_id=chat.id,
            role=MessageRole.ASSISTANT,
            content=assistant_response,
        )

        self.message_repository.create(
            assistant_message,
        )

        return user_message