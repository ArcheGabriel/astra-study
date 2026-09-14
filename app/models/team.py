from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.organisation import Organisation
    from app.models.team_membership import TeamMembership


class Team(Base, TimestampMixin):
    """
    SQLAlchemy model representing a team.

    A team belongs to exactly one organisation. Team names are unique
    within their organisation, not globally.
    """

    __tablename__ = "teams"

    __table_args__ = (
        UniqueConstraint(
            "organisation_id",
            "name",
            name="uq_teams_organisation_id_name",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisations.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    organisation: Mapped["Organisation"] = relationship(
        back_populates="teams",
    )

    memberships: Mapped[list["TeamMembership"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
    )

    documents: Mapped[list["Document"]] = relationship(
        back_populates="team",
    )
