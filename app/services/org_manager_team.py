from app.enums.organisation import OrgRole
from app.exceptions.document import TeamNotFoundError
from app.exceptions.team import (
    OrgManagerJurisdictionForbiddenError,
    TargetNotOrgManagerError,
)
from app.exceptions.user import UserNotFoundError
from app.repositories.org_manager_team import OrgManagerTeamRepository
from app.repositories.team import TeamRepository
from app.repositories.user import UserRepository
from app.retrieval.access import AccessContext
from app.schemas.team import OrgManagerTeamResponse


class OrgManagerTeamService:
    """
    Handles Org Manager jurisdiction grant/revoke (RBAC-5J): the
    many-to-many supervisory relationship between an ``OrgRole.MANAGER``
    and the teams they oversee.

    Deliberately a third, independent service alongside ``TeamService``
    (org-role-gated team creation/listing) and ``TeamMembershipService``
    (per-team-manager-gated membership mutation) -- jurisdiction has yet
    a different authorization model: only ``OrgRole.ADMIN`` may grant or
    revoke it, never a ``TeamRole.MANAGER``, never the target's own
    ``OrgRole.MANAGER`` status, and never anything derived from
    ``TeamMembership`` or ``AccessContext.team_ids``.

    Jurisdiction is structurally independent of ``TeamMembership``: a
    grant never creates, and a revoke never touches, a
    ``TeamMembership`` row.
    """

    def __init__(
        self,
        org_manager_team_repository: OrgManagerTeamRepository,
        team_repository: TeamRepository,
        user_repository: UserRepository,
    ) -> None:
        self.org_manager_team_repository = org_manager_team_repository
        self.team_repository = team_repository
        self.user_repository = user_repository

    def grant_jurisdiction(
        self,
        *,
        access: AccessContext,
        team_id: int,
        user_id: int,
    ) -> OrgManagerTeamResponse:
        """
        Grant ``user_id`` jurisdiction over ``team_id``.

        Only ``access.role == OrgRole.ADMIN`` may call this. ``team_id``
        and ``user_id`` must both belong to the ADMIN's own organisation,
        and ``user_id`` must currently hold ``OrgRole.MANAGER``.
        """

        self._authorize_admin(access=access)
        self._resolve_team(team_id=team_id, access=access)
        target_user = self._resolve_target_user(user_id=user_id, access=access)
        self._require_org_manager(target_user)

        jurisdiction = self.org_manager_team_repository.grant(
            user_id=user_id,
            team_id=team_id,
        )

        return OrgManagerTeamResponse.model_validate(jurisdiction)

    def revoke_jurisdiction(
        self,
        *,
        access: AccessContext,
        team_id: int,
        user_id: int,
    ) -> None:
        """
        Revoke ``user_id``'s jurisdiction over ``team_id``.

        Only ``access.role == OrgRole.ADMIN`` may call this. Same
        resolution/authorization ordering as ``grant_jurisdiction``.
        """

        self._authorize_admin(access=access)
        self._resolve_team(team_id=team_id, access=access)
        target_user = self._resolve_target_user(user_id=user_id, access=access)
        self._require_org_manager(target_user)

        self.org_manager_team_repository.revoke(
            user_id=user_id,
            team_id=team_id,
        )

    def _authorize_admin(
        self,
        *,
        access: AccessContext,
    ) -> None:
        """
        Confirm the acting user is ``OrgRole.ADMIN``.

        Runs first, before any database read tied to the request --
        never based on ``TeamMembership``, ``TeamRole``,
        ``AccessContext.team_ids``, or the target user's own role.
        """

        if access.role != OrgRole.ADMIN:
            raise OrgManagerJurisdictionForbiddenError()

    def _resolve_team(
        self,
        *,
        team_id: int,
        access: AccessContext,
    ) -> None:
        """
        Confirm ``team_id`` exists in the ADMIN's own organisation.

        Nonexistent team and cross-organisation team collapse into the
        same ``TeamNotFoundError`` (404) -- mirrors
        ``TeamMembershipService._resolve_team``'s existing
        enumeration-safety precedent.
        """

        team = self.team_repository.get_by_id(team_id)

        if team is None or team.organisation_id != access.organisation_id:
            raise TeamNotFoundError()

    def _resolve_target_user(
        self,
        *,
        user_id: int,
        access: AccessContext,
    ):
        """
        Confirm the target user exists in the ADMIN's own organisation,
        and return it.

        Nonexistent user and cross-organisation user collapse into the
        same ``UserNotFoundError`` (404), for the same enumeration-safety
        reason as ``_resolve_team``.
        """

        user = self.user_repository.get_by_id(user_id)

        if user is None or user.organisation_id != access.organisation_id:
            raise UserNotFoundError()

        return user

    def _require_org_manager(
        self,
        target_user,
    ) -> None:
        """
        Confirm the target user currently holds ``OrgRole.MANAGER``.

        Jurisdiction is only ever assignable to an actual Org Manager --
        checked against the target's *current* role, resolved fresh
        above, never a stale or client-supplied value.
        """

        if target_user.role != OrgRole.MANAGER:
            raise TargetNotOrgManagerError()
