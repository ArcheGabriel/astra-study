from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import TimestampMixin


class OrgManagerTeam(Base, TimestampMixin):
    """
    SQLAlchemy model representing an ``OrgRole.MANAGER``'s jurisdiction
    over a team.

    A purely supervisory relationship, structurally independent of
    ``TeamMembership``: a user may hold jurisdiction over a team without
    ever appearing as a ``TeamMembership`` row for it, and vice versa.
    Many-to-many by construction -- one Org Manager may hold jurisdiction
    over multiple teams, and one team may be under multiple Org Managers'
    jurisdiction. There is no ``role`` column (jurisdiction is a single
    binary state, unlike ``TeamMembership.role``) and no relationship to
    ``User``/``Team`` ORM objects -- every read goes through
    ``OrgManagerTeamRepository``'s explicit queries, so no lazy-load
    traversal is needed here.
    """

    __tablename__ = "org_manager_teams"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "team_id",
            name="uq_org_manager_teams_user_id_team_id",
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
