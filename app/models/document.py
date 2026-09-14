from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.enums.document import DocumentAccessScope, DocumentStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.organisation import Organisation
    from app.models.team import Team
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

    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisations.id"),
        nullable=False,
        index=True,
    )

    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id"),
        nullable=True,
        index=True,
    )

    access_scope: Mapped[DocumentAccessScope] = mapped_column(
        Enum(
            DocumentAccessScope,
            values_callable=lambda enum: [member.value for member in enum],
            name="documentaccessscope",
        ),
        default=DocumentAccessScope.INDIVIDUAL,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="documents",
    )

    organisation: Mapped["Organisation"] = relationship(
        back_populates="documents",
    )

    team: Mapped["Team | None"] = relationship(
        back_populates="documents",
    )