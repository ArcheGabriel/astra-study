from app.exceptions.chat import ChatNotFoundError
from app.models.chat import ChatSession
from app.repositories.chat import ChatRepository


class ChatService:
    """
    Handles business logic for chat sessions.
    """

    def __init__(
        self,
        chat_repository: ChatRepository,
    ) -> None:
        self.chat_repository = chat_repository

    def create_chat(
        self,
        user_id: int,
    ) -> ChatSession:
        """
        Create a new chat session.
        """

        chat_session = ChatSession(
            title="New Chat",
            user_id=user_id,
        )

        return self.chat_repository.create(
            chat_session,
        )

    def get_chat(
        self,
        chat_id: int,
        user_id: int,
    ) -> ChatSession:
        """
        Return a chat session owned by the user.
        """

        chat_session = self.chat_repository.get_by_id(
            chat_id,
        )

        if (
            chat_session is None
            or chat_session.user_id != user_id
        ):
            raise ChatNotFoundError()

        return chat_session

    def list_chats(
        self,
        user_id: int,
    ) -> list[ChatSession]:
        """
        Return all chat sessions belonging to the user.
        """

        return self.chat_repository.get_all_by_user_id(
            user_id,
        )

    def rename_chat(
        self,
        chat_id: int,
        user_id: int,
        title: str,
    ) -> ChatSession:
        """
        Rename a chat session.
        """

        chat_session = self.get_chat(
            chat_id,
            user_id,
        )

        chat_session.title = title

        return self.chat_repository.update(
            chat_session,
        )

    def delete_chat(
        self,
        chat_id: int,
        user_id: int,
    ) -> None:
        """
        Delete a chat session.
        """

        chat_session = self.get_chat(
            chat_id,
            user_id,
        )

        self.chat_repository.delete(
            chat_session,
        )