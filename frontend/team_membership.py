from __future__ import annotations

from frontend.models.user import User

MANAGER_ROLE = "manager"


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
