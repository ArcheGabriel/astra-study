"""
Executable specification for the frontend roster/search-result models
introduced for RBAC Phase B.1 -- ``TeamRosterMember`` (``GET
/teams/{team_id}/members``) and ``UserSearchResult`` (``GET /users?q=``).
"""

from __future__ import annotations

from frontend.models.team import TeamRosterMember
from frontend.models.user import UserSearchResult


def test_team_roster_member_parses_all_fields():
    member = TeamRosterMember.from_dict(
        {
            "user_id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "role": "manager",
        },
    )

    assert member == TeamRosterMember(
        user_id=1,
        username="alice",
        email="alice@example.com",
        role="manager",
    )


def test_team_roster_member_preserves_member_role():
    member = TeamRosterMember.from_dict(
        {
            "user_id": 2,
            "username": "bob",
            "email": "bob@example.com",
            "role": "member",
        },
    )

    assert member.role == "member"


def test_user_search_result_parses_all_fields():
    result = UserSearchResult.from_dict(
        {
            "id": 3,
            "username": "carol",
            "email": "carol@example.com",
        },
    )

    assert result == UserSearchResult(
        id=3,
        username="carol",
        email="carol@example.com",
    )
