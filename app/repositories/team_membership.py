from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.team_membership import TeamMembership
from app.repositories.base import BaseRepository


class TeamMembershipRepository(BaseRepository[TeamMembership]):
    """
    Repository for TeamMembership database operations.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        super().__init__(
            db=db,
            model=TeamMembership,
        )

    def get_team_ids_by_user_id(
        self,
        user_id: int,
    ) -> list[int]:
        """
        Return the ids of every team the given user is a member of.

        Selects only the ``team_id`` column -- never loads full
        TeamMembership rows when only the ids are needed.
        """

        statement = select(TeamMembership.team_id).where(
            TeamMembership.user_id == user_id
        )

        result = self.db.execute(statement)

        return [team_id for (team_id,) in result.all()]

    def get_membership(
        self,
        *,
        user_id: int,
        team_id: int,
    ) -> TeamMembership | None:
        """
        Return the membership row for one (user, team) pair, if any.

        Used to resolve the per-team ``TeamRole`` (manager vs. plain
        member) for an authorization decision -- e.g. whether a user may
        delete a TEAM-scoped document -- which ``AccessContext.team_ids``
        deliberately does not carry (it is a flat set of team ids, not a
        role map).
        """

        statement = select(TeamMembership).where(
            TeamMembership.user_id == user_id,
            TeamMembership.team_id == team_id,
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def get_memberships_with_team_by_user_id(
        self,
        user_id: int,
    ) -> list[TeamMembership]:
        """
        Return every TeamMembership row for a user, with its Team eagerly
        loaded in the same query (``joinedload``) -- avoids one lazy-load
        query per membership when a caller needs ``team_id``/team name/
        ``role`` together (e.g. the ``GET /users/me`` profile).

        Ordered by ``team_id`` ascending for a deterministic response --
        ``team_id`` is unique per user (``TeamMembership``'s own
        ``UniqueConstraint`` on ``(user_id, team_id)``), so this order
        never depends on insertion order or string collation.
        """

        statement = (
            select(TeamMembership)
            .where(TeamMembership.user_id == user_id)
            .options(joinedload(TeamMembership.team))
            .order_by(TeamMembership.team_id)
        )

        result = self.db.execute(statement)

        return list(result.scalars().unique().all())
