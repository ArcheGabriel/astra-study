"""
Executable specification for ``frontend.team_membership.is_org_admin``
(RBAC-9) -- the UX gate deciding whether the Org Manager
jurisdiction-management panel is shown.

This is a UX-only safeguard; the backend
(``OrgManagerTeamService._authorize_admin``) remains the sole authority
and independently re-enforces ``OrgRole.ADMIN`` on every grant/revoke
request. These tests exist to lock in that the frontend gate never
substitutes ``TeamRole.MANAGER`` membership, plain ``OrgRole.MANAGER``,
or existing Org Manager jurisdiction itself for actual ``OrgRole.ADMIN``
-- mirroring ``tests/frontend/test_team_membership_authorization.py``'s
structure for the analogous per-team gate.
"""

from __future__ import annotations

from frontend.models.user import ManagedTeam, TeamMembership, User
from frontend.team_membership import is_org_admin


def _user(
    *,
    role: str = "member",
    teams: list[TeamMembership] | None = None,
    managed_teams: list[ManagedTeam] | None = None,
) -> User:
    return User(
        id=1,
        username="alice",
        email="alice@example.com",
        organisation_id=7,
        role=role,
        teams=teams or [],
        managed_teams=managed_teams or [],
    )


def test_org_admin_is_authorized():
    user = _user(role="admin")

    assert is_org_admin(user) is True


def test_plain_member_is_not_authorized():
    user = _user(role="member")

    assert is_org_admin(user) is False


def test_org_manager_without_admin_role_is_not_authorized():
    """
    Plain ``OrgRole.MANAGER`` grants no jurisdiction-mutation authority
    -- mirrors the backend's ``OrgManagerJurisdictionForbiddenError``
    precedent exactly (only ``OrgRole.ADMIN`` may grant/revoke).
    """

    user = _user(role="manager")

    assert is_org_admin(user) is False


def test_team_manager_without_admin_role_is_not_authorized():
    """
    Being a team's own ``TeamRole.MANAGER`` grants no jurisdiction
    authority either.
    """

    user = _user(
        role="member",
        teams=[TeamMembership(team_id=1, team_name="Research", role="manager")],
    )

    assert is_org_admin(user) is False


def test_existing_jurisdiction_without_admin_role_is_not_authorized():
    """
    Already holding jurisdiction over a team (``managed_teams``) grants
    no authority to grant/revoke jurisdiction for anyone -- only
    ``OrgRole.ADMIN`` may mutate ``OrgManagerTeam``.
    """

    user = _user(
        role="manager",
        managed_teams=[ManagedTeam(team_id=1, team_name="Research")],
    )

    assert is_org_admin(user) is False


def test_no_user_is_not_authorized():
    assert is_org_admin(None) is False
