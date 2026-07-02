from sqlalchemy import select
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