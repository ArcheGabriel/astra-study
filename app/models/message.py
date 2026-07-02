from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.enums.message import MessageRole
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.chat import ChatSession


class ChatMessage(Base, TimestampMixin):
    """
    Represents a single message within a chat session.
    """

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    chat_session_id: Mapped[int] = mapped_column(
        ForeignKey("chat_sessions.id"),
        nullable=False,
        index=True,
    )

    role: Mapped[MessageRole] = mapped_column(
        Enum(
            MessageRole,
            values_callable=lambda enum: [member.value for member in enum],
            name="messagerole",
        ),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    chat_session: Mapped["ChatSession"] = relationship(
        back_populates="messages",
    )