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


class MessageService:
    """
    Business logic for chat messages.
    """

    def __init__(
        self,
        chat_repository: ChatRepository,
        message_repository: MessageRepository,
    ):
        self.chat_repository = chat_repository
        self.message_repository = message_repository

    def create_message(
        self,
        *,
        chat_id: int,
        current_user: User,
        message_data: MessageCreate,
    ) -> MessageResponse:
        """
        Create a new user message within a chat session.
        """

        chat = self.chat_repository.get_by_id(chat_id)

        if chat is None or chat.user_id != current_user.id:
            raise ChatNotFoundError()

        message = ChatMessage(
            chat_session_id=chat.id,
            role=MessageRole.USER,
            content=message_data.content,
        )

        created_message = self.message_repository.create(
            message,
        )

        return MessageResponse.model_validate(
            created_message,
        )

    def get_messages(
        self,
        *,
        chat_id: int,
        current_user: User,
    ) -> list[MessageResponse]:
        """
        Retrieve all messages for a chat session.
        """

        chat = self.chat_repository.get_by_id(chat_id)

        if chat is None or chat.user_id != current_user.id:
            raise ChatNotFoundError()

        messages = self.message_repository.get_by_chat_session(
            chat_id,
        )

        return [
            MessageResponse.model_validate(
                message,
            )
            for message in messages
        ]