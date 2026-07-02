from sqlalchemy import desc, select
from sqlalchemy.orm import Session

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