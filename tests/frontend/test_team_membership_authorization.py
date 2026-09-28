"""
Executable specification for ``frontend.team_membership.is_team_manager``
-- the UX gate deciding whether the team-management panel is shown.

This is a UX-only safeguard; the backend
(``TeamMembershipService._authorize_team_manager``) remains the sole
authority and independently re-enforces the identical rule on every
request. These tests exist to lock in that the frontend gate never
substitutes ``OrgRole`` or Org Manager jurisdiction for actual per-team
``TeamRole.MANAGER`` membership -- mirroring the exact RBAC
distinctions the backend's own Phase B.0 test suite requires.
"""

from __future__ import annotations

from frontend.models.user import ManagedTeam, TeamMembership, User
from frontend.team_membership import is_team_manager


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


def test_team_manager_on_the_exact_team_is_authorized():
    user = _user(teams=[TeamMembership(team_id=1, team_name="Research", role="manager")])

    assert is_team_manager(user, 1) is True


def test_team_member_on_the_exact_team_is_not_authorized():
    user = _user(teams=[TeamMembership(team_id=1, team_name="Research", role="member")])

    assert is_team_manager(user, 1) is False


def test_manager_of_a_different_team_is_not_authorized():
    user = _user(teams=[TeamMembership(team_id=2, team_name="Support", role="manager")])

    assert is_team_manager(user, 1) is False


def test_org_admin_without_team_membership_is_not_authorized():
    """
    OrgRole.ADMIN grants no team-membership-management authority --
    mirrors the backend's TeamMembershipOperationForbiddenError
    precedent exactly.
    """

    user = _user(role="admin", teams=[])

    assert is_team_manager(user, 1) is False


def test_org_manager_without_team_membership_is_not_authorized():
    """
    OrgRole.MANAGER (org-wide) alone grants no team-membership-management
    authority either.
    """

    user = _user(role="manager", teams=[])

    assert is_team_manager(user, 1) is False


def test_org_manager_jurisdiction_without_team_membership_is_not_authorized():
    """
    Org Manager jurisdiction (``managed_teams``) governs Qdrant/SQL
    document read-visibility only -- it must never grant team
    membership-management authority.
    """

    user = _user(
        role="manager",
        teams=[],
        managed_teams=[ManagedTeam(team_id=1, team_name="Research")],
    )

    assert is_team_manager(user, 1) is False


def test_no_user_is_not_authorized():
    assert is_team_manager(None, 1) is False


def test_team_manager_with_unrelated_other_memberships_is_authorized_only_for_their_team():
    user = _user(
        teams=[
            TeamMembership(team_id=1, team_name="Research", role="manager"),
            TeamMembership(team_id=2, team_name="Support", role="member"),
        ],
    )

    assert is_team_manager(user, 1) is True
    assert is_team_manager(user, 2) is False
