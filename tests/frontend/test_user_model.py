"""
Executable specification for the frontend ``User`` model's parsing of the
``GET /users/me`` response -- in particular that ``managed_teams`` (Org
Manager jurisdiction) survives the round trip that previously dropped it.
"""

from __future__ import annotations

from frontend.models.user import ManagedTeam, TeamMembership, User


def _profile(**overrides: object) -> dict:
    base = {
        "id": 1,
        "username": "alice",
        "email": "alice@example.com",
        "organisation_id": 7,
        "role": "member",
        "teams": [],
        "managed_teams": [],
    }
    base.update(overrides)
    return base


def test_teams_are_parsed_with_team_role():
    data = _profile(
        teams=[
            {"team_id": 1, "team_name": "Research", "role": "manager"},
        ],
    )

    user = User.from_dict(data)

    assert user.teams == [
        TeamMembership(team_id=1, team_name="Research", role="manager"),
    ]


def test_managed_teams_are_parsed():
    data = _profile(
        managed_teams=[
            {"team_id": 2, "team_name": "Support"},
        ],
    )

    user = User.from_dict(data)

    assert user.managed_teams == [
        ManagedTeam(team_id=2, team_name="Support"),
    ]


def test_empty_teams_produces_empty_list():
    user = User.from_dict(_profile(teams=[]))

    assert user.teams == []


def test_empty_managed_teams_produces_empty_list():
    user = User.from_dict(_profile(managed_teams=[]))

    assert user.managed_teams == []


def test_missing_managed_teams_key_defaults_to_empty_list():
    """
    A response predating RBAC-5J (no ``managed_teams`` key at all) must
    not raise -- it should parse as an empty list, matching ``teams``'
    existing ``.get(..., [])`` behavior.
    """

    data = _profile()
    del data["managed_teams"]

    user = User.from_dict(data)

    assert user.managed_teams == []


def test_teams_and_managed_teams_remain_independent():
    data = _profile(
        teams=[
            {"team_id": 1, "team_name": "Design", "role": "member"},
        ],
        managed_teams=[
            {"team_id": 2, "team_name": "Research"},
        ],
    )

    user = User.from_dict(data)

    assert [t.team_id for t in user.teams] == [1]
    assert [t.team_id for t in user.managed_teams] == [2]
