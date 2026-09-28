from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions.team import (
    OrgManagerJurisdictionAlreadyExistsError,
    OrgManagerJurisdictionNotFoundError,
)
from app.models.org_manager_team import OrgManagerTeam
from app.models.team import Team
from app.repositories.base import BaseRepository


class OrgManagerTeamRepository(BaseRepository[OrgManagerTeam]):
    """
    Repository for OrgManagerTeam (RBAC-5J jurisdiction) database
    operations.

    Deliberately mirrors ``TeamMembershipRepository``'s shape: the two
    tables represent structurally independent relationships (membership
    vs. supervisory jurisdiction), so their repositories follow the same
    query/mutation patterns without sharing any code -- jurisdiction
    never reads or writes a ``TeamMembership`` row, and vice versa.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        super().__init__(
            db=db,
            model=OrgManagerTeam,
        )

    def get_jurisdiction(
        self,
        *,
        user_id: int,
        team_id: int,
    ) -> OrgManagerTeam | None:
        """
        Return the jurisdiction row for one (Org Manager, team) pair,
        if any -- the direct analog of
        ``TeamMembershipRepository.get_membership``.
        """

        statement = select(OrgManagerTeam).where(
            OrgManagerTeam.user_id == user_id,
            OrgManagerTeam.team_id == team_id,
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def get_team_ids_by_user_id(
        self,
        user_id: int,
    ) -> list[int]:
        """
        Return the ids of every team the given user holds jurisdiction
        over -- the direct analog of
        ``TeamMembershipRepository.get_team_ids_by_user_id``, consumed
        by ``get_access_context`` to populate
        ``AccessContext.jurisdiction_team_ids``.
        """

        statement = select(OrgManagerTeam.team_id).where(
            OrgManagerTeam.user_id == user_id,
        )

        result = self.db.execute(statement)

        return [team_id for (team_id,) in result.all()]

    def get_by_team_id(
        self,
        team_id: int,
    ) -> list[OrgManagerTeam]:
        """
        Return every jurisdiction row for the given team, ordered by
        ``user_id`` ascending for a deterministic response -- consumed
        by ``GET /teams/{team_id}/managers``. Reads only
        ``org_manager_teams``; never touches ``TeamMembership``.
        """

        statement = (
            select(OrgManagerTeam)
            .where(OrgManagerTeam.team_id == team_id)
            .order_by(OrgManagerTeam.user_id)
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    def get_jurisdictions_with_team_by_user_id(
        self,
        user_id: int,
    ) -> list[tuple[int, str]]:
        """
        Return every ``(team_id, team_name)`` pair the given user holds
        jurisdiction over, ordered by ``team_id`` ascending for a
        deterministic response -- consumed by ``GET /users/me`` to build
        ``managed_teams``.

        A plain join against ``Team`` for the name, rather than an ORM
        relationship traversal: ``OrgManagerTeam`` deliberately carries
        no ``relationship()`` to ``Team``/``User`` (see its model
        docstring), so this is the one place that needs the team name
        alongside the id, resolved with an explicit join instead.
        """

        statement = (
            select(OrgManagerTeam.team_id, Team.name)
            .join(Team, Team.id == OrgManagerTeam.team_id)
            .where(OrgManagerTeam.user_id == user_id)
            .order_by(OrgManagerTeam.team_id)
        )

        result = self.db.execute(statement)

        return [(team_id, team_name) for team_id, team_name in result.all()]

    def grant(
        self,
        *,
        user_id: int,
        team_id: int,
    ) -> OrgManagerTeam:
        """
        Grant ``user_id`` jurisdiction over ``team_id``.

        Raises ``OrgManagerJurisdictionAlreadyExistsError`` if the pair
        already has a jurisdiction row. The pre-check is a fast path,
        not the sole guard: two concurrent grants for the same pair
        could both pass it, so the insert itself is wrapped in the same
        TOCTOU-guarding pattern as
        ``TeamRepository.create_with_initial_manager`` /
        ``TeamMembershipRepository.add_membership`` -- if the
        ``(user_id, team_id)`` unique constraint is violated at flush,
        the session is rolled back and the failure is translated
        instead of a raw, unhandled ``IntegrityError``. Any other
        ``IntegrityError`` cause is re-raised unchanged (narrow
        translation only).
        """

        existing = self.get_jurisdiction(
            user_id=user_id,
            team_id=team_id,
        )

        if existing is not None:
            raise OrgManagerJurisdictionAlreadyExistsError()

        jurisdiction = OrgManagerTeam(
            user_id=user_id,
            team_id=team_id,
        )

        try:
            self.db.add(jurisdiction)

            # SQLite raises the unique-constraint violation on the
            # INSERT itself, at flush -- not at the later commit -- so
            # this whole sequence (not just the final commit) must be
            # inside the guard.
            self.db.flush()

            self.db.commit()

        except IntegrityError as exc:

            self.db.rollback()

            message = str(exc.orig) if exc.orig is not None else str(exc)

            if (
                "org_manager_teams.user_id" in message
                and "org_manager_teams.team_id" in message
            ):
                raise OrgManagerJurisdictionAlreadyExistsError() from exc

            raise

        self.db.refresh(jurisdiction)

        return jurisdiction

    def revoke(
        self,
        *,
        user_id: int,
        team_id: int,
    ) -> None:
        """
        Revoke ``user_id``'s jurisdiction over ``team_id``.

        Raises ``OrgManagerJurisdictionNotFoundError`` if no such
        jurisdiction row exists. Unlike
        ``TeamMembershipRepository.remove_membership``, there is no
        minimum-jurisdiction-holder invariant to protect -- a team may
        validly have zero Org Managers overseeing it (its operational
        management continues via ``TeamRole.MANAGER`` regardless) -- so
        a plain fetch-then-delete is safe: two concurrent revokes of the
        same grant are naturally serialized by SQLite's writer lock, and
        the second one simply finds nothing left to delete.
        """

        jurisdiction = self.get_jurisdiction(
            user_id=user_id,
            team_id=team_id,
        )

        if jurisdiction is None:
            raise OrgManagerJurisdictionNotFoundError()

        self.db.delete(jurisdiction)
        self.db.commit()
