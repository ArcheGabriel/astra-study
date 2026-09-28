from __future__ import annotations

from frontend.models.user import User

MANAGER_ROLE = "manager"

# Mirrors app/enums/organisation.py::OrgRole.ADMIN's exact string value --
# same constant value as frontend.access_scope.ADMIN_ROLE, duplicated
# here (rather than imported) so this module stays free of any
# upload-scope-specific dependency; both mirror the one backend enum
# value, not two independent policies.
_ADMIN_ROLE = "admin"


def is_org_admin(
    user: User | None,
) -> bool:
    """
    True only if ``user`` holds ``OrgRole.ADMIN`` at the organisation
    level.

    UX gate only -- the backend independently and authoritatively
    re-enforces ``OrgRole.ADMIN`` on every Org Manager jurisdiction
    grant/revoke request (``OrgManagerTeamService._authorize_admin``),
    regardless of what this function returns. Sourced from
    ``user.role`` only -- the same representation
    ``frontend.access_scope.can_select_organisation_scope`` already
    uses for the identical ``OrgRole.ADMIN`` check, extracted here as a
    small, directly testable function rather than an inline condition,
    since the jurisdiction-management panel is gated on it.
    """

    if user is None:
        return False

    return user.role == _ADMIN_ROLE


def is_team_manager(
    user: User | None,
    team_id: int,
) -> bool:
    """
    True only if ``user`` holds ``TeamRole.MANAGER`` on this *specific*
    team, via an actual ``TeamMembership`` row.

    UX gate only -- the backend independently and authoritatively
    re-enforces the identical rule (``TeamMembershipService.
    _authorize_team_manager``) on every roster/add/remove/promote
    request, regardless of what this function returns.

    Deliberately sourced from ``user.teams`` only. Never
    ``user.role`` (``OrgRole`` -- ``OrgRole.ADMIN``/``OrgRole.MANAGER``
    grant no direct membership-management authority anywhere in this
    system) and never ``user.managed_teams`` (Org Manager jurisdiction,
    which governs Qdrant/SQL document read-visibility only, never
    membership authority) -- mirrors the exact same exclusions already
    established in ``frontend.access_scope.selectable_teams``.
    """

    if user is None:
        return False

    return any(
        membership.team_id == team_id
        and membership.role == MANAGER_ROLE
        for membership in user.teams
    )
