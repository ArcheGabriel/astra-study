from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.enums.document import DocumentStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Document(
    Base,
    TimestampMixin,
):
    """
    Represents an uploaded document.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        nullable=False,
    )

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(
            DocumentStatus,
            values_callable=lambda enum: [member.value for member in enum],
            name="documentstatus",
        ),
        default=DocumentStatus.UPLOADED,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="documents",
    )