"""
Executable specification for ``frontend.team_membership.can_create_team``
-- the UX gate deciding whether the team-creation form is shown.

This is a UX-only safeguard; the backend (``TeamService.create_team``)
remains the sole authority and independently re-enforces the identical
rule (``OrgRole.MEMBER`` rejected before any database read) on every
``POST /teams`` request, regardless of what this function returns.
"""

from __future__ import annotations

from frontend.models.user import ManagedTeam, TeamMembership, User
from frontend.team_membership import can_create_team


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


def test_org_admin_can_create_team():
    user = _user(role="admin")

    assert can_create_team(user) is True


def test_org_manager_can_create_team():
    user = _user(role="manager")

    assert can_create_team(user) is True


def test_org_member_cannot_create_team():
    user = _user(role="member")

    assert can_create_team(user) is False


def test_no_user_cannot_create_team():
    assert can_create_team(None) is False


def test_team_role_manager_without_org_role_manager_cannot_create_team():
    """
    A ``TeamRole.MANAGER`` membership alone (no org-wide ``OrgRole``
    beyond MEMBER) does not grant team-creation authority -- team
    creation is an org-wide capability, not a per-team one.
    """

    user = _user(
        role="member",
        teams=[TeamMembership(team_id=1, team_name="Research", role="manager")],
    )

    assert can_create_team(user) is False


def test_org_manager_jurisdiction_alone_does_not_change_the_result():
    """
    Org Manager jurisdiction (``managed_teams``) is a distinct,
    structurally independent concept from ``OrgRole`` -- it must not be
    consulted here (an ``OrgRole.MANAGER`` is already sufficient on its
    own; jurisdiction should neither add nor remove that).
    """

    user = _user(
        role="manager",
        managed_teams=[ManagedTeam(team_id=1, team_name="Research")],
    )

    assert can_create_team(user) is True
