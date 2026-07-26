from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.message import ChatMessage
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[ChatMessage]):
    """
    Repository for ChatMessage database operations.
    """

    def __init__(
        self,
        db: Session,
    ):
        super().__init__(
            db=db,
            model=ChatMessage,
        )

    def get_by_chat_session(
        self,
        chat_session_id: int,
    ) -> list[ChatMessage]:
        """
        Retrieve all messages belonging to a chat session.

        Messages are returned in chronological order.
        """

        statement = (
            select(ChatMessage)
            .where(
                ChatMessage.chat_session_id == chat_session_id,
            )
            .order_by(
                ChatMessage.created_at.asc(),
            )
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    def get_recent_messages(
        self,
        *,
        chat_session_id: int,
        limit: int,
    ) -> list[ChatMessage]:
        """
        Retrieve the most recent messages from a chat session.

        Returned in chronological order.
        """

        statement = (
            select(ChatMessage)
            .where(
                ChatMessage.chat_session_id == chat_session_id,
            )
            .order_by(
                desc(ChatMessage.created_at),
            )
            .limit(limit)
        )

        result = self.db.execute(statement)

        messages = list(result.scalars().all())

        messages.reverse()

        return messages