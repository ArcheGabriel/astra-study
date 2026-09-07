from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.enums.message import MessageRole
from app.models.message import ChatMessage
from app.repositories.base import BaseRepository

# Roles that make up the user-visible conversation. Message counting for the
# rolling-summary feature is deliberately limited to these so that any
# infrastructure message types introduced later (system / tool / retrieval
# bookkeeping) cannot silently shift the summary boundaries.
CONVERSATIONAL_ROLES: tuple[MessageRole, ...] = (
    MessageRole.USER,
    MessageRole.ASSISTANT,
)


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

        Messages are returned in chronological order. Ordering is by primary
        key rather than ``created_at`` because ``created_at`` is only
        second-precision on SQLite and rapidly-exchanged messages can share a
        timestamp, which would make the order (and any window slicing built on
        it) non-deterministic.
        """

        statement = (
            select(ChatMessage)
            .where(
                ChatMessage.chat_session_id == chat_session_id,
            )
            .order_by(
                ChatMessage.id.asc(),
            )
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    def get_conversational_messages(
        self,
        chat_session_id: int,
    ) -> list[ChatMessage]:
        """
        Retrieve the user + assistant messages of a chat session in order.

        This is the authoritative sequence used for summary boundaries and for
        the rolling generation window.
        """

        statement = (
            select(ChatMessage)
            .where(
                ChatMessage.chat_session_id == chat_session_id,
                ChatMessage.role.in_(CONVERSATIONAL_ROLES),
            )
            .order_by(
                ChatMessage.id.asc(),
            )
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    def count_conversational_messages(
        self,
        chat_session_id: int,
    ) -> int:
        """
        Count the user + assistant messages of a chat session.
        """

        statement = (
            select(func.count())
            .select_from(ChatMessage)
            .where(
                ChatMessage.chat_session_id == chat_session_id,
                ChatMessage.role.in_(CONVERSATIONAL_ROLES),
            )
        )

        return int(self.db.execute(statement).scalar_one())

    def count_conversational_messages_before(
        self,
        *,
        chat_session_id: int,
        timestamp: datetime,
    ) -> int:
        """
        Count the user + assistant messages created at or before ``timestamp``.

        ``timestamp`` is ``chat_sessions.summary_updated_at``, which is now the
        exact ``created_at`` of the last message included in the stored summary
        (not a wall-clock write time), so that message must itself count as
        covered -- hence ``<=`` rather than ``<``.

        SQLite stores ``created_at`` at second precision while production
        PostgreSQL keeps sub-second precision. On SQLite a message sharing the
        cursor's whole second can therefore be counted as covered even if it
        arrived just after the summary snapshot; the reverse can also happen and
        a same-second message gets conservatively re-included in the next
        delta. Both are harmless because the summary generator is merge-based
        (previous summary + new delta) and never re-summarizes from scratch.
        """

        statement = (
            select(func.count())
            .select_from(ChatMessage)
            .where(
                ChatMessage.chat_session_id == chat_session_id,
                ChatMessage.role.in_(CONVERSATIONAL_ROLES),
                ChatMessage.created_at <= timestamp,
            )
        )

        return int(self.db.execute(statement).scalar_one())

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
                desc(ChatMessage.id),
            )
            .limit(limit)
        )

        result = self.db.execute(statement)

        messages = list(result.scalars().all())

        messages.reverse()

        return messages
