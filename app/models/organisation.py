from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.team import Team
    from app.models.user import User


class Organisation(Base, TimestampMixin):
    """
    SQLAlchemy model representing an organisation.

    Every user belongs to exactly one organisation. Deleting an
    organisation is not a supported operation in this phase -- no
    relationship below cascades a delete onto users, teams, or documents.
    """

    __tablename__ = "organisations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="organisation",
    )

    teams: Mapped[list["Team"]] = relationship(
        back_populates="organisation",
    )

    documents: Mapped[list["Document"]] = relationship(
        back_populates="organisation",
    )
