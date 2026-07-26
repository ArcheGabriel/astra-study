from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.exceptions.chat import ChatNotFoundError
from app.models.chat import ChatSession
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatSession]):
    """
    Repository for ChatSession database operations.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        super().__init__(
            db=db,
            model=ChatSession,
        )

    def get_all_by_user_id(
        self,
        user_id: int,
    ) -> list[ChatSession]:
        """
        Return all chat sessions belonging to a user.
        """

        statement = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.updated_at))
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    def update_title(
        self,
        chat_id: int,
        title: str,
    ) -> ChatSession:
        """
        Update the title of a chat session.
        """

        chat = self.get_by_id(chat_id)

        if chat is None:
            raise ChatNotFoundError()

        chat.title = title

        self.db.commit()
        self.db.refresh(chat)

        return chat

    def update_summary(
        self,
        *,
        chat_id: int,
        summary: str,
    ) -> ChatSession:
        """
        Update the rolling summary of a chat session.
        """

        chat = self.get_by_id(chat_id)

        if chat is None:
            raise ChatNotFoundError()

        chat.summary = summary
        chat.summary_updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(chat)

        return chat