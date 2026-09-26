from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.enums.team import TeamRole
from app.exceptions.team import TeamNameAlreadyExistsError
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    """
    Repository for Team database operations.

    Deliberately minimal: beyond ``get_by_id`` (inherited from
    ``BaseRepository``), only the queries/transaction RBAC-5H actually
    needs -- team management (rename/delete) is out of scope; see
    RBAC-5E's and RBAC-5H's investigation reports.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        super().__init__(
            db=db,
            model=Team,
        )

    def get_by_organisation_and_name(
        self,
        *,
        organisation_id: int,
        name: str,
    ) -> Team | None:
        """
        Pre-check for the ``(organisation_id, name)`` unique constraint,
        so a duplicate raises a clean ``TeamNameAlreadyExistsError``
        instead of a raw ``IntegrityError`` in the common case -- mirrors
        ``UserRepository.get_by_email``'s role in ``UserService.register``.

        This is a best-effort pre-check, not the source of truth for
        uniqueness: ``create_with_initial_manager`` also guards the
        commit itself against the TOCTOU race between this check and
        that commit (see its docstring).
        """

        statement = select(Team).where(
            Team.organisation_id == organisation_id,
            Team.name == name,
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def list_by_organisation(
        self,
        organisation_id: int,
    ) -> list[Team]:
        """
        Return every team in one organisation, ordered by ``id``
        ascending for a deterministic response. Membership is never a
        filter here -- listing a team never implies the requester
        belongs to it.
        """

        statement = (
            select(Team)
            .where(Team.organisation_id == organisation_id)
            .order_by(Team.id)
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    def create_with_initial_manager(
        self,
        *,
        organisation_id: int,
        name: str,
        creator_user_id: int,
    ) -> Team:
        """
        Atomically create a Team and its sole initial TeamMembership
        (``role=TeamRole.MANAGER``, owned by the creator) in one
        transaction -- both rows persist together or neither does, so a
        team can never exist without a manager, even under failure.

        Guards the commit against the TOCTOU race between the service's
        ``get_by_organisation_and_name`` pre-check and this commit: if
        the commit itself fails on the ``(organisation_id, name)``
        unique constraint, the session is rolled back and the failure is
        translated into ``TeamNameAlreadyExistsError`` -- never a raw
        ``IntegrityError``, and never left in a failed-transaction
        session state. Any other ``IntegrityError`` cause is re-raised
        unchanged (narrow translation only, per this project's existing
        error-handling conventions).
        """

        team = Team(
            organisation_id=organisation_id,
            name=name,
        )

        try:
            self.db.add(team)

            # The (organisation_id, name) unique constraint is violated
            # here, at flush -- SQLite raises on the INSERT itself, not
            # at the later commit -- so this whole sequence (not just
            # the final commit) must be inside the guard.
            self.db.flush()

            membership = TeamMembership(
                user_id=creator_user_id,
                team_id=team.id,
                role=TeamRole.MANAGER,
            )

            self.db.add(membership)

            self.db.commit()

        except IntegrityError as exc:

            self.db.rollback()

            message = str(exc.orig) if exc.orig is not None else str(exc)

            if "teams.organisation_id" in message and "teams.name" in message:
                raise TeamNameAlreadyExistsError() from exc

            raise

        self.db.refresh(team)

        return team
