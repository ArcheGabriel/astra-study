from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.enums.team import TeamRole
from app.exceptions.team import (
    LastTeamManagerError,
    TeamMemberNotFoundError,
    TeamMembershipAlreadyExistsError,
)
from app.models.team_membership import TeamMembership
from app.models.user import User
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

    def get_memberships_with_user_by_team_id(
        self,
        team_id: int,
    ) -> list[TeamMembership]:
        """
        Return every ``TeamMembership`` row for one team, with its
        ``User`` eagerly loaded in the same query (``joinedload``) --
        avoids one lazy-load query per member when a caller needs
        ``user_id``/username/email/``role`` together (the team roster).

        Ordered by the member's username ascending -- deterministic
        regardless of membership insertion order, and a natural sort for
        a management UI browsing a roster.
        """

        statement = (
            select(TeamMembership)
            .where(TeamMembership.team_id == team_id)
            .join(TeamMembership.user)
            .options(joinedload(TeamMembership.user))
            .order_by(User.username)
        )

        result = self.db.execute(statement)

        return list(result.scalars().unique().all())

    def count_managers(
        self,
        *,
        team_id: int,
        exclude_user_id: int | None = None,
    ) -> int:
        """
        Count a team's current ``TeamRole.MANAGER`` memberships.

        ``exclude_user_id`` lets a manager-removal check ask "how many
        *other* managers would remain" without first deleting anything
        -- used by ``remove_membership`` to decide, before mutating
        anything, whether removing this specific manager would leave
        the team with zero.
        """

        statement = select(func.count()).select_from(TeamMembership).where(
            TeamMembership.team_id == team_id,
            TeamMembership.role == TeamRole.MANAGER,
        )

        if exclude_user_id is not None:
            statement = statement.where(
                TeamMembership.user_id != exclude_user_id,
            )

        return self.db.execute(statement).scalar_one()

    def add_membership(
        self,
        *,
        user_id: int,
        team_id: int,
    ) -> TeamMembership:
        """
        Add ``user_id`` to ``team_id`` as a plain ``TeamRole.MEMBER``.

        Raises ``TeamMembershipAlreadyExistsError`` if a membership row
        already exists for this ``(user_id, team_id)`` pair (at either
        role) -- there is no "re-add" or role-changing effect here; use
        ``promote_to_manager`` to change an existing member's role.

        The pre-check below is a fast path, not the sole guard: two
        concurrent adds for the same pair could both pass it, so the
        insert itself is wrapped in the same TOCTOU-guarding pattern as
        ``TeamRepository.create_with_initial_manager`` -- if the
        ``(user_id, team_id)`` unique constraint is violated at flush,
        the session is rolled back and the failure is translated into
        ``TeamMembershipAlreadyExistsError`` instead of a raw,
        unhandled ``IntegrityError``. Any other ``IntegrityError`` cause
        is re-raised unchanged (narrow translation only).
        """

        existing = self.get_membership(
            user_id=user_id,
            team_id=team_id,
        )

        if existing is not None:
            raise TeamMembershipAlreadyExistsError()

        membership = TeamMembership(
            user_id=user_id,
            team_id=team_id,
            role=TeamRole.MEMBER,
        )

        try:
            self.db.add(membership)

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
                "team_memberships.user_id" in message
                and "team_memberships.team_id" in message
            ):
                raise TeamMembershipAlreadyExistsError() from exc

            raise

        self.db.refresh(membership)

        return membership

    def promote_to_manager(
        self,
        *,
        user_id: int,
        team_id: int,
    ) -> TeamMembership:
        """
        Promote an existing ``TeamRole.MEMBER`` to ``TeamRole.MANAGER``
        in place -- same membership row, only ``role`` changes.

        Raises ``TeamMemberNotFoundError`` if no membership row exists
        for this ``(user_id, team_id)`` pair, and
        ``TeamMembershipAlreadyExistsError`` if it already holds
        ``TeamRole.MANAGER`` -- there is no ``MANAGER -> MEMBER``
        demotion anywhere in this codebase (see RBAC-5I's frozen
        team-role lifecycle), so this method only ever moves a
        membership forward from MEMBER to MANAGER, never back.
        """

        membership = self.get_membership(
            user_id=user_id,
            team_id=team_id,
        )

        if membership is None:
            raise TeamMemberNotFoundError()

        if membership.role == TeamRole.MANAGER:
            raise TeamMembershipAlreadyExistsError()

        membership.role = TeamRole.MANAGER

        self.db.commit()
        self.db.refresh(membership)

        return membership

    def remove_membership(
        self,
        *,
        user_id: int,
        team_id: int,
    ) -> None:
        """
        Remove a ``(user_id, team_id)`` membership entirely, regardless
        of its current role.

        Raises ``TeamMemberNotFoundError`` if no such membership exists.
        A ``TeamRole.MEMBER`` removal has no invariant to protect and is
        deleted directly. This is always a full removal, never a
        demotion -- ``MANAGER -> MEMBER`` does not exist as an operation
        anywhere.

        For a ``TeamRole.MANAGER``, the last-manager invariant is
        enforced by the DELETE statement itself, not by a prior
        ``SELECT count(...)`` followed by a separate DELETE: the
        remaining-manager count is embedded as a correlated subquery in
        the DELETE's own ``WHERE`` clause, so SQLite evaluates "does
        another manager exist" and "remove this row" as one indivisible
        write. This closes the race a read-then-write split cannot: two
        concurrent removals of two *different* managers on the same
        two-manager team would, under a prior read-then-delete design,
        both observe "one other manager remains" before either
        committed, and both would succeed -- leaving zero managers. With
        the count embedded in the write itself, SQLite's single-writer
        lock serializes the two DELETE statements, and the second one's
        subquery is evaluated fresh, after the first has already
        committed -- so it correctly sees zero *other* managers and
        deletes nothing. If the conditional DELETE affects no row, a
        follow-up existence check distinguishes "already gone"
        (``TeamMemberNotFoundError``) from "blocked by the invariant"
        (``LastTeamManagerError``) without trusting any earlier read.
        """

        membership = self.get_membership(
            user_id=user_id,
            team_id=team_id,
        )

        if membership is None:
            raise TeamMemberNotFoundError()

        if membership.role != TeamRole.MANAGER:
            self.db.delete(membership)
            self.db.commit()
            return

        other_managers_exist = (
            select(func.count())
            .select_from(TeamMembership)
            .where(
                TeamMembership.team_id == team_id,
                TeamMembership.role == TeamRole.MANAGER,
                TeamMembership.user_id != user_id,
            )
            .scalar_subquery()
        )

        conditional_delete = delete(TeamMembership).where(
            TeamMembership.user_id == user_id,
            TeamMembership.team_id == team_id,
            TeamMembership.role == TeamRole.MANAGER,
            other_managers_exist > 0,
        )

        result = self.db.execute(conditional_delete)

        self.db.commit()

        if result.rowcount > 0:
            return

        # The atomic conditional delete removed nothing. Re-check fresh
        # (never trust the read at the top of this method, which could
        # now be stale) to report the correct reason: the membership is
        # gone entirely, or it survived because removing it would have
        # left the team with zero managers.
        still_present = self.get_membership(
            user_id=user_id,
            team_id=team_id,
        )

        if still_present is None:
            raise TeamMemberNotFoundError()

        raise LastTeamManagerError()
