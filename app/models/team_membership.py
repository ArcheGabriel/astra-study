from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.enums.team import TeamRole
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.user import User


class TeamMembership(Base, TimestampMixin):
    """
    SQLAlchemy model representing a user's membership in a team.

    A user may hold at most one membership row per team (enforced by a
    unique constraint), and may belong to multiple teams. ``role`` is the
    membership's own role (team manager vs. plain member) -- independent
    of the user's organisation-scoped ``OrgRole``.
    """

    __tablename__ = "team_memberships"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "team_id",
            name="uq_team_memberships_user_id_team_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
    )

    role: Mapped[TeamRole] = mapped_column(
        Enum(
            TeamRole,
            values_callable=lambda enum: [member.value for member in enum],
            name="teamrole",
        ),
        default=TeamRole.MEMBER,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="team_memberships",
    )

    team: Mapped["Team"] = relationship(
        back_populates="memberships",
    )
