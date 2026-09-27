"""
Executable specification for ``frontend.access_scope`` -- the pure,
Streamlit-free logic backing the document-upload access-scope UI.

Covers the required RBAC-Phase-A matrix: which teams are selectable for a
TEAM-scoped upload, who may select ORGANISATION, and the UX-level
validation of scope/team combinations. This is a UX safeguard only -- the
backend (``DocumentService._can_create``) remains the authoritative
authorization layer.
"""

from __future__ import annotations

from frontend.access_scope import (
    INDIVIDUAL,
    ORGANISATION,
    TEAM,
    can_select_organisation_scope,
    selectable_teams,
    validate_upload_scope,
)
from frontend.models.user import ManagedTeam, TeamMembership, User


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


# --------------------------------------------------------------------------- #
# selectable_teams
# --------------------------------------------------------------------------- #


def test_selectable_teams_includes_member_team():
    membership = TeamMembership(team_id=1, team_name="Research", role="member")
    user = _user(teams=[membership])

    assert selectable_teams(user) == [membership]


def test_selectable_teams_includes_manager_team():
    membership = TeamMembership(team_id=1, team_name="Research", role="manager")
    user = _user(teams=[membership])

    assert selectable_teams(user) == [membership]


def test_selectable_teams_excludes_jurisdiction_only_team():
    """
    Org Manager jurisdiction (``managed_teams``) without an actual
    ``TeamMembership`` must not make a team selectable for TEAM upload --
    TEAM document creation requires real membership.
    """

    user = _user(
        role="manager",
        teams=[],
        managed_teams=[ManagedTeam(team_id=1, team_name="Research")],
    )

    assert selectable_teams(user) == []


def test_selectable_teams_ignores_organisation_wide_teams_not_joined():
    """
    ``selectable_teams`` only ever reflects ``user.teams`` -- an
    organisation-wide team list (``GET /teams``) is never consulted here,
    so a team the user hasn't joined is never selectable regardless of
    how many other teams exist in the organisation.
    """

    user = _user(teams=[])

    assert selectable_teams(user) == []


def test_selectable_teams_empty_for_none_user():
    assert selectable_teams(None) == []


# --------------------------------------------------------------------------- #
# can_select_organisation_scope
# --------------------------------------------------------------------------- #


def test_admin_can_select_organisation_scope():
    assert can_select_organisation_scope(_user(role="admin")) is True


def test_manager_cannot_select_organisation_scope():
    assert can_select_organisation_scope(_user(role="manager")) is False


def test_member_cannot_select_organisation_scope():
    assert can_select_organisation_scope(_user(role="member")) is False


def test_none_user_cannot_select_organisation_scope():
    assert can_select_organisation_scope(None) is False


# --------------------------------------------------------------------------- #
# validate_upload_scope
# --------------------------------------------------------------------------- #


def test_individual_scope_always_valid():
    user = _user(role="member")

    assert validate_upload_scope(scope=INDIVIDUAL, team_id=None, user=user) is None


def test_team_scope_requires_a_team_selection():
    user = _user(teams=[TeamMembership(team_id=1, team_name="Research", role="member")])

    error = validate_upload_scope(scope=TEAM, team_id=None, user=user)

    assert error is not None


def test_team_scope_valid_for_actual_membership():
    membership = TeamMembership(team_id=1, team_name="Research", role="member")
    user = _user(teams=[membership])

    error = validate_upload_scope(scope=TEAM, team_id=1, user=user)

    assert error is None


def test_team_scope_invalid_for_team_outside_membership():
    membership = TeamMembership(team_id=1, team_name="Research", role="member")
    user = _user(teams=[membership])

    error = validate_upload_scope(scope=TEAM, team_id=999, user=user)

    assert error is not None


def test_organisation_scope_valid_for_admin():
    error = validate_upload_scope(
        scope=ORGANISATION,
        team_id=None,
        user=_user(role="admin"),
    )

    assert error is None


def test_organisation_scope_invalid_for_manager():
    error = validate_upload_scope(
        scope=ORGANISATION,
        team_id=None,
        user=_user(role="manager"),
    )

    assert error is not None


def test_organisation_scope_invalid_for_member():
    error = validate_upload_scope(
        scope=ORGANISATION,
        team_id=None,
        user=_user(role="member"),
    )

    assert error is not None
