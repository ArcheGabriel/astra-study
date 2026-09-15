from sqlalchemy import select
from sqlalchemy.orm import Session

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
