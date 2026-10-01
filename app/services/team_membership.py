import logging

from app.cache.semantic import SemanticRetrievalCache
from app.enums.team import TeamRole
from app.exceptions.document import TeamNotFoundError
from app.exceptions.team import TeamMembershipOperationForbiddenError
from app.exceptions.user import UserNotFoundError
from app.repositories.team import TeamRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.repositories.user import UserRepository
from app.retrieval.access import AccessContext
from app.schemas.team import TeamMemberResponse, TeamRosterMemberResponse

logger = logging.getLogger(__name__)


class TeamMembershipService:
    """
    Handles direct team-membership management (RBAC-5I): add member,
    remove member, promote MEMBER -> MANAGER, and remove MANAGER
    (subject to the last-manager invariant); plus roster retrieval
    (``list_members``, RBAC-Phase-B.0) so a manager can see whom to act
    on.

    Deliberately separate from ``TeamService``, which owns team creation
    and organisation-scoped listing only. The two services authorize
    against different models -- ``TeamService.create_team`` checks the
    actor's org-wide ``OrgRole``; every method here checks the actor's
    per-team ``TeamRole`` on the *specific* target team -- so keeping
    them apart avoids blurring two distinct authorization models into
    one class, matching ``TeamService``'s own docstring, which already
    defers membership management to this later stage.

    Authorization here is strict and non-negotiable: only the target
    team's own ``TeamRole.MANAGER`` may perform any of these four
    operations. ``OrgRole.ADMIN`` has no direct membership-mutation
    authority in this stage -- an ADMIN-initiated add is deferred to a
    later membership-request/approval-workflow milestone, not built
    here. ``OrgRole.MANAGER`` alone, without also being this specific
    team's ``TeamRole.MANAGER``, has no membership-management authority
    either -- holding an organisation-level role never substitutes for
    per-team operational authority.

    There is no ``MANAGER -> MEMBER`` demotion operation anywhere in
    this service (frozen team-role lifecycle) -- a manager only ever
    stops being one by being removed from the team entirely, and only
    when another manager remains to take over.
    """

    def __init__(
        self,
        team_membership_repository: TeamMembershipRepository,
        team_repository: TeamRepository,
        user_repository: UserRepository,
        semantic_cache: SemanticRetrievalCache | None = None,
    ) -> None:
        self.team_membership_repository = team_membership_repository
        self.team_repository = team_repository
        self.user_repository = user_repository
        # Optional (RBAC/C.3): see UserService's identical field -- a
        # membership add/remove/promote changes the target user's future
        # AccessContext.team_ids, so their semantic-retrieval-cache
        # entries must be invalidated. None (the default) skips this.
        self.semantic_cache = semantic_cache

    def _invalidate_cache_for(self, user_id: int) -> None:
        if self.semantic_cache is None:
            return
        try:
            self.semantic_cache.invalidate_user(user_id)
        except Exception:
            logger.exception(
                "Semantic retrieval cache invalidation failed after a "
                "team membership change for user_id=%s.",
                user_id,
            )

    def add_member(
        self,
        *,
        access: AccessContext,
        team_id: int,
        user_id: int,
    ) -> TeamMemberResponse:
        """
        Add ``user_id`` to ``team_id`` as a plain ``TeamRole.MEMBER``.

        Only ``team_id``'s own ``TeamRole.MANAGER`` may call this.
        ``user_id`` must belong to the same organisation as ``team_id``.
        """

        self._resolve_team(team_id=team_id, access=access)
        self._authorize_team_manager(access=access, team_id=team_id)
        self._resolve_target_user(user_id=user_id, access=access)

        membership = self.team_membership_repository.add_membership(
            user_id=user_id,
            team_id=team_id,
        )

        self._invalidate_cache_for(user_id)

        return TeamMemberResponse.model_validate(membership)

    def remove_member(
        self,
        *,
        access: AccessContext,
        team_id: int,
        user_id: int,
    ) -> None:
        """
        Remove ``user_id``'s membership from ``team_id`` entirely,
        regardless of its current role.

        Only ``team_id``'s own ``TeamRole.MANAGER`` may call this. If
        the target membership is a ``TeamRole.MANAGER``, the removal is
        rejected (``LastTeamManagerError``) unless another manager
        remains on the team afterward -- enforced atomically by
        ``TeamMembershipRepository.remove_membership``. This is never a
        demotion: a removed manager ends up with no membership row at
        all, never converted to ``TeamRole.MEMBER``.
        """

        self._resolve_team(team_id=team_id, access=access)
        self._authorize_team_manager(access=access, team_id=team_id)
        self._resolve_target_user(user_id=user_id, access=access)

        self.team_membership_repository.remove_membership(
            user_id=user_id,
            team_id=team_id,
        )

        self._invalidate_cache_for(user_id)

    def promote_member(
        self,
        *,
        access: AccessContext,
        team_id: int,
        user_id: int,
    ) -> TeamMemberResponse:
        """
        Promote ``user_id``'s existing ``TeamRole.MEMBER`` membership on
        ``team_id`` to ``TeamRole.MANAGER`` in place.

        Only ``team_id``'s own ``TeamRole.MANAGER`` may call this.
        """

        self._resolve_team(team_id=team_id, access=access)
        self._authorize_team_manager(access=access, team_id=team_id)
        self._resolve_target_user(user_id=user_id, access=access)

        membership = self.team_membership_repository.promote_to_manager(
            user_id=user_id,
            team_id=team_id,
        )

        self._invalidate_cache_for(user_id)

        return TeamMemberResponse.model_validate(membership)

    def list_members(
        self,
        *,
        access: AccessContext,
        team_id: int,
    ) -> list[TeamRosterMemberResponse]:
        """
        Return every member of ``team_id``, ordered by username
        ascending.

        Only ``team_id``'s own ``TeamRole.MANAGER`` may call this -- the
        exact same authorization boundary as add/remove/promote above
        (never ``OrgRole.ADMIN``, never ``OrgRole.MANAGER`` alone, never
        Org Manager jurisdiction), since the roster exists to support
        those same decisions (whom to promote/remove), not general team
        browsing by non-managers.
        """

        self._resolve_team(team_id=team_id, access=access)
        self._authorize_team_manager(access=access, team_id=team_id)

        memberships = (
            self.team_membership_repository.get_memberships_with_user_by_team_id(
                team_id,
            )
        )

        return [
            TeamRosterMemberResponse(
                user_id=membership.user_id,
                username=membership.user.username,
                email=membership.user.email,
                role=membership.role,
            )
            for membership in memberships
        ]

    def _resolve_team(
        self,
        *,
        team_id: int,
        access: AccessContext,
    ) -> None:
        """
        Confirm ``team_id`` exists in the requester's own organisation.

        Nonexistent team and cross-organisation team collapse into the
        same ``TeamNotFoundError`` (404) -- mirrors
        ``DocumentService._can_create``'s TEAM branch, so a requester
        can never enumerate another organisation's team ids.
        """

        team = self.team_repository.get_by_id(team_id)

        if team is None or team.organisation_id != access.organisation_id:
            raise TeamNotFoundError()

    def _authorize_team_manager(
        self,
        *,
        access: AccessContext,
        team_id: int,
    ) -> None:
        """
        Confirm the acting user is specifically ``team_id``'s own
        ``TeamRole.MANAGER``.

        Resolved via a direct, targeted membership lookup -- never from
        ``AccessContext.team_ids``, which carries no per-team role --
        mirroring ``DocumentService._can_delete``'s existing pattern for
        resolving per-team ``TeamRole`` authority.
        """

        membership = self.team_membership_repository.get_membership(
            user_id=access.user_id,
            team_id=team_id,
        )

        if membership is None or membership.role != TeamRole.MANAGER:
            raise TeamMembershipOperationForbiddenError()

    def _resolve_target_user(
        self,
        *,
        user_id: int,
        access: AccessContext,
    ) -> None:
        """
        Confirm the target user exists in the requester's own
        organisation.

        Nonexistent user and cross-organisation user collapse into the
        same ``UserNotFoundError`` (404), for the same enumeration-safety
        reason as ``_resolve_team``.
        """

        user = self.user_repository.get_by_id(user_id)

        if user is None or user.organisation_id != access.organisation_id:
            raise UserNotFoundError()
